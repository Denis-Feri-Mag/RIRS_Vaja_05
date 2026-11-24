---
name: nova-api-tocka
description: Dodaj ali spremeni Flask REST pot v obstoječem blueprintu, z JWT zaščito, JSON odgovorom in pytest testi po vzoru tega projekta. Uporabi, ko je treba dodati novo končno točko pod /api/ ali dopolniti obstoječo.
---

# Nova API točka

Pred spremembo preberi `AGENTS.md`, ustrezno specifikacijo v `docs/specs/` in obstoječi blueprint. Ne spreminjaj sheme v `backend/init_db.py` brez potrditve uporabnika.

## Kje kaj je

- Blueprinti so v `backend/app/`, npr. `rezervacije.py` z `url_prefix="/api/rezervacije"`.
- Dekorator `samo("vloga")` je v `backend/app/auth.py`. Administrator ima dostop tudi do poti drugih vlog.
- Nov blueprint je treba registrirati v `backend/app/__init__.py`.
- JSON pomočniki in preverjanje vnosov naj ostanejo v istem slogu kot v obstoječi datoteki, npr. `kot_json` in `preberi_dan`.

## Koraki

1. Poišči blueprint, ki že pokriva to področje. Novega dodaj samo, če res ne spada nikamor.
2. Določi pot, metodo in vlogo. Pot naj bo kratka in v slovenščini, kot so že `/odpoved` in `/zakljucek`.
3. Preberi telo z `request.get_json()` ali parametre iz poti. Napačen vnos vrni z `jsonify(napaka="..."), 400`.
4. Če zapis ne obstaja ali ni od tega uporabnika, vrni 404 z `napaka`. Če zmanjka pravice, 403. Konflikt, npr. zasedena miza, je 409.
5. Uspešen zapis shrani z `db.session.commit()` in vrni JSON. Pri ustvarjanju uporabi kodo 201.
6. Dodaj teste v `backend/tests/test_*.py` po skillu `pisanje-testov`. Če datoteka za to področje že obstaja, teste dodaj tja.
7. Po spremembi poženi `ruff check .` in `pytest` v mapi `backend`.

Predloge sta v tej mapi: `predloga-tocka.txt` in `predloga-test.txt`. Ju prilagodi, ne kopiraj slepo.
