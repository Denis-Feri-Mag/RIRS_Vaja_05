#!/usr/bin/env python3
"""PostToolUse hook. Na spremenjeni datoteki požene ruff ali eslint --fix."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def nalozi():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def tool_input(data):
    vrednost = data.get("toolInput", data.get("tool_input", {}))
    return vrednost if isinstance(vrednost, dict) else {}


def poti_iz(obj, zbrane=None):
    if zbrane is None:
        zbrane = []
    if isinstance(obj, dict):
        for kljuc, vrednost in obj.items():
            if kljuc.lower() in {"path", "file_path", "filepath", "file", "filename"} and isinstance(vrednost, str):
                zbrane.append(vrednost)
            else:
                poti_iz(vrednost, zbrane)
    elif isinstance(obj, list):
        for element in obj:
            poti_iz(element, zbrane)
    return zbrane


def koren(data):
    kandidati = [
        os.environ.get("GROK_WORKSPACE_ROOT"),
        data.get("workspaceRoot"),
        data.get("workspace_root"),
        data.get("cwd"),
    ]
    for kandidat in kandidati:
        if kandidat:
            return Path(kandidat).resolve()
    return Path.cwd().resolve()


def preskoci(rel):
    prepoved = {"node_modules", ".venv", "venv", "dist", "coverage", "__pycache__", ".git", ".ruff_cache"}
    return any(delcek in prepoved for delcek in rel.parts)


def pozeni(ukaz, cwd):
    try:
        subprocess.run(ukaz, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired):
        pass


def popravi(root, pot):
    pot = Path(pot)
    if not pot.is_absolute():
        pot = (root / pot).resolve()
    else:
        pot = pot.resolve()
    try:
        rel = pot.relative_to(root)
    except ValueError:
        return
    if not pot.is_file() or preskoci(rel):
        return
    if pot.suffix == ".py":
        ruff = shutil.which("ruff")
        if ruff:
            konfiguracija = root / "backend" / "ruff.toml"
            ukaz = [ruff, "check", "--fix"]
            if konfiguracija.is_file():
                ukaz.extend(["--config", str(konfiguracija)])
            ukaz.append(str(pot))
            pozeni(ukaz, root)
        return
    if pot.suffix in {".js", ".jsx", ".ts", ".tsx"} and "frontend" in rel.parts:
        frontend = root / "frontend"
        if not frontend.is_dir():
            return
        npx = shutil.which("npx")
        if not npx:
            return
        try:
            relativna = pot.relative_to(frontend)
        except ValueError:
            relativna = pot
        pozeni([npx, "eslint", "--fix", str(relativna)], frontend)


def main():
    data = nalozi()
    root = koren(data)
    for pot in poti_iz(tool_input(data)):
        popravi(root, pot)
    sys.exit(0)


if __name__ == "__main__":
    main()
