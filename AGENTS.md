# Navodila za agenta

Projekt Glass: spletna aplikacija za en lokal. Frontend je React z Vite, backend Flask z PostgreSQL. Ukaze poženi iz korena repozitorija, razen kjer je naveden `cd`.

## Namestitev in zagon

Backend:

```
cd backend
python -m venv .venv
```

Windows: `.venv\Scripts\activate`
Linux in macOS: `source .venv/bin/activate`

```
pip install -r requirements-dev.txt
cp .env.example .env
python init_db.py --seed
flask run
```

API teče na http://localhost:5000. V `.env` sta `DATABASE_URL` in `JWT_SECRET`. Lokalno potrebuješ PostgreSQL z bazo `glass`.

Frontend:

```
cd frontend
npm install
npm start
```

Vmesnik teče na http://localhost:5173. V `frontend/.env` je lahko `VITE_API_URL`.

## Lint in testi

Pred zaključkom spremembe vedno poženi lint in teste. Če kaj pade, popravi pred oddajo.

Backend (potreben je PostgreSQL, za teste baza `glass_test`):

```
cd backend
ruff check .
pytest
```

Za pytest nastavi `TEST_DATABASE_URL`, npr. `postgresql+psycopg://UPORABNIK@127.0.0.1:5432/glass_test`. V CI je še `JWT_SECRET`.

Frontend:

```
cd frontend
npm run lint
npm test
```

Pokritost: `npm run test:coverage`. Build: `npm run build`.

## Struktura

- `backend/app/` Flask API, blueprinti in modeli
- `backend/tests/` pytest testi
- `backend/init_db.py` shema in začetni podatki
- `frontend/src/` React strani in komponenti, testi ob izvornih datotekah
- `docs/` dokumentacija, `docs/adr/` odločitve, `docs/wireframes/`, `docs/specs/` specifikacije novih zgodb
- `.github/workflows/ci-cd.yml` pipeline
- `fly.toml` in `backend/Dockerfile` namestitev backend
- `.grok/` skilli, hooki, dovoljenja in MCP za Grok Build

## Dokumentacija

Pred delom na funkcionalnosti preberi `docs/05-uporabniske-zgodbe.md` in ustrezno specifikacijo v `docs/specs/`, če obstaja. Za stanje MVP glej `docs/07-pregled-projekta.md`. Modele spreminjaj šele po `docs/03-podatkovni-model.md`. Novo knjižnico ali spremembo sklada preveri v `docs/adr/` in `docs/04-arhitektura-in-tehnoloski-sklad.md`. Obseg je v `docs/02-funkcionalnosti-in-obseg.md`.

## Konvencije

Imena v kodi sledijo obstoječemu slogu. Domenski pojmi so v slovenščini, npr. rezervacija, narocilo, jed, vloga. Datoteke strani so npr. `Prijava.jsx` in `MojeRezervacije.jsx`. Poti API so pod `/api/`, telo odgovora je JSON. Napaka gre v polje `napaka` s primerno kodo (400, 403, 404, 409).

Za zaščito poti uporabi dekorator `samo` iz `app.auth`. Administrator sme tudi poti drugih vlog, ker tako že dela `samo`. Prijavo preverjaj z JWT, na frontendu kliči `api` iz `api.js`.

Nov blueprint registriraj v `backend/app/__init__.py`. Testi backend so v `backend/tests/test_*.py`, uporabljajo fiksturi `client` in `podatki` ter pomožni `token` in `glava`. Frontend testi so Vitest in Testing Library, `fetch` se nadomesti z `vi.stubGlobal`.

## Česa ne spreminjaj brez potrditve

Brez izrecnega dovoljenja uporabnika ne spreminjaj:

- `.github/workflows/`
- `fly.toml`
- `backend/Dockerfile`
- sheme in začetnih podatkov v `backend/init_db.py`
- datotek `.env` in `.env.*`, razen `.env.example` če je res treba
- nastavitev za Vercel

Skrivnosti v kodo in v git ne spadajo.

## Varnostne omejitve

Grok Build bere dovoljenja iz `.grok/config.toml`. Prepovedano je branje in urejanje `.env`, zasebnih ključev (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`) ter ukazi `rm -rf` in `git push --force` oziroma `git push -f`.

Hooki so v `.grok/hooks/`. Pred orodjem `safety_check.py` zavrne nevarne ukaze in branje skrivnosti. Po urejanju `format_changed.py` požene `ruff check --fix` za Python in `eslint --fix` za frontend. Projektne hooke je treba potrditi z `/hooks-trust` ali zagonom `grok --trust`.
