# Tehnični načrt: 001 Prihod gosta

## Izhodišče

Zgodba iz `docs/specs/001-prihod-gosta/spec.md` doda natakarju oznako prihoda na obstoječi rezervaciji. Status `gost_prisel` je že v omejitvi modela `Rezervacija` in v `backend/init_db.py`. `kot_json` ga že vrača. `MojeRezervacije.jsx` ima napis »gost je prišel«. Pot, ki status nastavi, ne obstaja. `miza_prosta` in `GET /api/rezervacije/dan` gledata samo `potrjena`. `zakljucek` sprejme samo `potrjena`. Na seznamu dneva je pri vsaki vrstici samo gumb Zaključi.

Zasedenost mize je že za ves UTC-dan začetka, ne za 120-minutno okno. Isti dan pomeni isto pravilo: `zacetek.astimezone(UTC).date()` v `miza_prosta`.

## Obseg

Spremenijo se samo:

- `backend/app/rezervacije.py`
- `backend/tests/test_rezervacije.py`
- `frontend/src/Natakar.jsx`
- nov `frontend/src/Natakar.test.jsx`
- nov `frontend/src/MojeRezervacije.test.jsx`

Shema, `init_db.py`, `models.py`, blueprinti, `miza.status`, naročila in dokumenti `docs/03`, `docs/05`, `docs/07` ostanejo. Prihod ne zasede mize v tabeli `miza` in ne odpre naročila. Administrator gre skozi obstoječi dekorator `samo`.

## API

Vse v blueprintu `rezervacije`, predloga iz `.grok/skills/nova-api-tocka`.

### `POST /api/rezervacije/<id>/prihod`

- `@samo("natakar")`. Uspeh je 200 in telo `kot_json` s `"status": "gost_prisel"`.
- Ni zapisa: 404, `napaka` = »Rezervacija ne obstaja.«
- Status ni `potrjena`: 400, `napaka` = »Prihod lahko označite samo pri potrjeni rezervaciji.« Status se ne spremeni.
- Gost in kuhar: 403. Brez žetona: 401, kot ga vrne `verify_jwt_in_request`.
- Administrator: 200, ker `samo` to že dovoli.

### `GET /api/rezervacije/dan`

Filter statusa postane `potrjena` ali `gost_prisel`. Odpovedane in zaključene ostanejo zunaj. V vsakem objektu ostanejo `id`, `ura`, `stevilka_mize`, `ime`, `priimek`, `opomba` in se doda `status`. Ura ostane UTC `HH:MM`. Vrstni red ostane po `zacetek`.

### Zasedenost mize

V `miza_prosta` naj pogoj statusa zajame `potrjena` in `gost_prisel`. Ista funkcija hrani `POST /api/rezervacije` (409, »Miza ni prosta.«) in `GET /api/rezervacije/mize`.

### Zaključek in odpoved

`zakljucek` sprejme `potrjena` in `gost_prisel`, nato nastavi `zakljucena`. Drug status ostane 400 z obstoječim besedilom »Rezervacija ni odprta.«

`odpoved` se ne spreminja. Za `gost_prisel` že vrne 400 in statusa ne zapiše. To samo pokrije test.

Po zaključku `miza_prosta` mizo spet spusti, ker `zakljucena` ni v filtru.

## Vmesnik

### Natakar

Na vsaki vrstici seznama dneva izpiši status: `potrjena` kot »potrjena«, `gost_prisel` kot »gost je prišel«. Zemljevid naj bo ločen od obstoječega `STATUS` za postavke naročila.

Pri `potrjena` pokaži gumb »Prihod« in obstoječi »Zaključi«. Klik na Prihod takoj pokliče `POST /api/rezervacije/{id}/prihod` prek `api` in znova naloži seznam dneva. Med klicem je gumb onemogočen. Napaka gre v obstoječe polje `napaka`. Potrditvenega pogovornega okna za prihod ni.

Pri `gost_prisel` gumba Prihod ni. Gumb Zaključi in njegov pogovor ostaneta. Zaključek še vedno kliče `/zakljucek` in osveži seznam.

### Moje rezervacije

Komponente ne spreminjaj. `gost_prisel` že pade v Zgodovina, napis je »gost je prišel«, `onOdpovej` pa dobijo samo vrstice s statusom `potrjena`. Sprejemni kriterij 9 to izpolni. Test to zaklene.

## Testi

Po `.grok/skills/pisanje-testov`. Imena brez šumnikov.

Backend, v `test_rezervacije.py`, fiksturi `client` in `podatki`, pomočnika `token` in `glava`:

- `test_prihod_gosta`: natakar na `potrjena` dobi 200 in `gost_prisel`; ponovni klic 400; neobstoječ id 404; gost in kuhar 403; brez žetona 401; administrator 200.
- `test_dan_vkljucuje_prispele`: seznam dneva vsebuje `potrjena` in `gost_prisel` s poljem `status`; `odpovedana` in `zakljucena` manjkata.
- `test_prispela_rezervacija_drzi_mizo`: ista miza isti dan vrne 409; odpoved gosta vrne 400 in status ostane `gost_prisel`; zaključek natakarja vrne 200 in `zakljucena`; nova rezervacija iste mize nato uspe.

Frontend, Vitest in Testing Library, `fetch` z `vi.stubGlobal`, v `afterEach` `vi.unstubAllGlobals`:

- `Natakar.test.jsx`: vrstica `potrjena` pokaže Prihod in Zaključi; klik Prihod pošlje `POST /api/rezervacije/{id}/prihod`. Vrstica `gost_prisel` pokaže »gost je prišel« in Zaključi, gumba Prihod ni. `fetch` naj po URL razloči `/api/rezervacije/dan`, mize, jedilnik in zalogi, ki jih stran ob zagonu kliče.
- `MojeRezervacije.test.jsx`: rezervacija `gost_prisel` pokaže »gost je prišel« in nima gumba Odpovej. Rezervacija `potrjena` gumb Odpovej še ima.

## Preverjanje ob implementaciji

V `backend`: `ruff check .` in `pytest` (baza `glass_test`, `TEST_DATABASE_URL`).

V `frontend`: `npm run lint` in `npm test`.

V brskalniku, ko tečeta API in Vite: natakar označi prihod na potrjeni rezervaciji, vidi status in zaključi; gost na Moje rezervacije vidi »gost je prišel« brez Odpovej. Preveri tudi, da nova rezervacija iste mize istega dne pred zaključkom ne uspe in po zaključku uspe.
