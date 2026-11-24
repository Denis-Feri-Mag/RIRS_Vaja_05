#!/usr/bin/env python3
"""PreToolUse hook. Zavrne nevarne ukaze in dostop do skrivnosti."""

import json
import re
import sys


def allow():
    sys.exit(0)


def deny(reason):
    sys.stdout.write(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False) + "\n")
    sys.exit(0)


def nalozi():
    raw = sys.stdin.read()
    if not raw.strip():
        allow()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        allow()


def tool_input(data):
    vrednost = data.get("toolInput", data.get("tool_input", {}))
    return vrednost if isinstance(vrednost, dict) else {}


def ukaz_iz(data):
    vhod = tool_input(data)
    for kljuc in ("command", "cmd", "bash", "shell"):
        vrednost = vhod.get(kljuc)
        if isinstance(vrednost, str):
            return vrednost
    return ""


def poti_iz(obj, zbrane=None):
    if zbrane is None:
        zbrane = []
    if isinstance(obj, dict):
        for kljuc, vrednost in obj.items():
            if kljuc.lower() in {"path", "file_path", "filepath", "file", "filename", "target"} and isinstance(
                vrednost, str
            ):
                zbrane.append(vrednost)
            else:
                poti_iz(vrednost, zbrane)
    elif isinstance(obj, list):
        for element in obj:
            poti_iz(element, zbrane)
    return zbrane


def ime_datoteke(pot):
    return pot.replace("\\", "/").rstrip("/").split("/")[-1]


def je_skrivnost(pot):
    ime = ime_datoteke(pot)
    if ime == ".env":
        return True
    if ime.startswith(".env.") and ime != ".env.example":
        return True
    if ime.endswith(".pem") or ime.endswith(".key"):
        return True
    if ime in {"id_rsa", "id_ed25519", "id_dsa", "id_ecdsa"}:
        return True
    return False


RM_RF = re.compile(r"\brm\s+(?:-[^\s]*r[^\s]*f|-[^\s]*f[^\s]*r|--recursive\s+--force|--force\s+--recursive)\b")
GIT_FORCE = re.compile(r"\bgit\s+push\b", re.I)
GIT_FORCE_ZASTAVICA = re.compile(r"(?:^|\s)(?:--force-with-lease|--force|-f)(?:\s|$)")
BRANJE = re.compile(
    r"\b(cat|less|more|head|tail|type|Get-Content|gc|Get-Content\.exe|notepad|vim|nano|open|xdg-open)\b",
    re.I,
)


def nevaren_ukaz(ukaz):
    if RM_RF.search(ukaz):
        return "Ukaza rm -rf ne smem zagnati."
    if GIT_FORCE.search(ukaz) and GIT_FORCE_ZASTAVICA.search(ukaz):
        return "Ukaza git push --force ne smem zagnati."
    if BRANJE.search(ukaz):
        for delcek in re.split(r"\s+", ukaz):
            ocisceno = delcek.strip("\"'")
            if je_skrivnost(ocisceno):
                return "Skrivnih datotek ne smem brati."
    for delcek in re.split(r"\s+", ukaz):
        ocisceno = delcek.strip("\"'")
        if je_skrivnost(ocisceno) and re.search(r"\b(cat|less|more|head|tail|type|Get-Content|gc)\b", ukaz, re.I):
            return "Skrivnih datotek ne smem brati."
    return None


def main():
    data = nalozi()
    ukaz = ukaz_iz(data)
    if ukaz:
        razlog = nevaren_ukaz(ukaz)
        if razlog:
            deny(razlog)
    for pot in poti_iz(tool_input(data)):
        if je_skrivnost(pot):
            deny("Skrivnih datotek ne smem brati ali urejati.")
    allow()


if __name__ == "__main__":
    main()
