# Naloge: 001 Prihod gosta

Vir sta `spec.md` in `plan.md`. Naloge so v izvedbenem vrstnem redu. Shema, `init_db.py`, `models.py`, `MojeRezervacije.jsx`, `miza.status` in naročila ostanejo nespremenjeni.

N2 in N3 sledita N1, ker testa status `gost_prisel` nastavita prek nove poti. N4 in N5 lahko tečeta vzporedno z N1–N3, ker `fetch` nadomestiš z `vi.stubGlobal`. N6 je zadnja.

## N1. Pot za prihod

**Datoteke:** `backend/app/rezervacije.py`, `backend/tests/test_rezervacije.py`

**Naredi:**

- V blueprint `rezervacije` dodaj `POST /<int:rezervacija_id>/prihod` z `@samo("natakar")`.
- Uspeh: status zapisa postane `gost_prisel`, odgovor je 200 in `kot_json`.
- Ni zapisa: 404, `napaka` = »Rezervacija ne obstaja.«
- Status ni `potrjena`: 400, `napaka` = »Prihod lahko označite samo pri potrjeni rezervaciji.« Status ostane.
- Dodaj `test_prihod_gosta`: natakar dobi 200 in `gost_prisel`; ponovni klic 400; neobstoječ id 404; gost in kuhar 403; brez žetona 401; administrator 200.

**Končano, ko:** veljajo sprejemni kriteriji 1, 2 in 3 ter dovoljenje administratorja iz zahteve 7.

## N2. Seznam rezervacij dneva

**Datoteke:** `backend/app/rezervacije.py`, `backend/tests/test_rezervacije.py`

**Odvisnost:** N1

**Naredi:**

- V `GET /api/rezervacije/dan` vključi statusa `potrjena` in `gost_prisel`. Odpovedane in zaključene ostanejo zunaj.
- V vsak objekt dodaj polje `status`. Obdrži `id`, `ura`, `stevilka_mize`, `ime`, `priimek` in `opomba`. Ura ostane UTC `HH:MM`, vrstni red po `zacetek`.
- Dodaj `test_dan_vkljucuje_prispele`.

**Končano, ko:** velja sprejemni kriterij 4.

## N3. Miza do zaključka

**Datoteke:** `backend/app/rezervacije.py`, `backend/tests/test_rezervacije.py`

**Odvisnost:** N1

**Naredi:**

- V `miza_prosta` štej statusa `potrjena` in `gost_prisel`. Dan ostane UTC-dan začetka. Ista funkcija hrani `POST /api/rezervacije` (409, »Miza ni prosta.«) in `GET /api/rezervacije/mize`.
- `zakljucek` sprejme `potrjena` in `gost_prisel`, nato nastavi `zakljucena`. Drug status ostane 400 z besedilom »Rezervacija ni odprta.«
- `odpoved` ne spreminjaj.
- Dodaj `test_prispela_rezervacija_drzi_mizo`: ista miza isti dan vrne 409; odpoved gosta vrne 400 in status ostane `gost_prisel`; zaključek natakarja vrne 200 in `zakljucena`; nova rezervacija iste mize nato uspe.

**Končano, ko:** veljajo sprejemni kriteriji 5, 6 in 7.

## N4. Seznam natakarja

**Datoteke:** `frontend/src/Natakar.jsx`, `frontend/src/Natakar.test.jsx`

**Naredi:**

- Na vsaki vrstici izpiši status. `potrjena` kot »potrjena«, `gost_prisel` kot »gost je prišel«. Zemljevid naj bo ločen od `STATUS` za postavke naročila.
- Pri `potrjena` pokaži gumb »Prihod« in obstoječi »Zaključi«. Klik na Prihod takoj pokliče `POST /api/rezervacije/{id}/prihod` prek `api` in znova naloži seznam dneva. Med klicem je gumb onemogočen. Napaka gre v obstoječe polje `napaka`. Potrditvenega okna za prihod ni.
- Pri `gost_prisel` gumba Prihod ni. Gumb Zaključi in njegov pogovor ostaneta.
- V `Natakar.test.jsx` pokrij oba prikaza in klik Prihod. `fetch` po URL razloči seznam dneva, mize, jedilnik in zalogi. V `afterEach` pokliči `vi.unstubAllGlobals`.

**Končano, ko:** velja sprejemni kriterij 8 in test v kriteriju 10 za ta vmesnik.

## N5. Prikaz pri gostu

**Datoteke:** `frontend/src/MojeRezervacije.test.jsx`

**Naredi:**

- Komponente ne spreminjaj. `gost_prisel` je že v Zgodovini, napis je »gost je prišel«, gumb Odpovej pa dobijo samo vrstice s statusom `potrjena`.
- Test: rezervacija `gost_prisel` pokaže »gost je prišel« in nima gumba Odpovej. Rezervacija `potrjena` gumb Odpovej še ima.
- `fetch` nadomesti z `vi.stubGlobal`. V `afterEach` pokliči `vi.unstubAllGlobals`.

**Končano, ko:** velja sprejemni kriterij 9.

## N6. Preverjanje

**Odvisnost:** N1–N5

**Naredi:**

- V `backend` poženi `ruff check .` in `pytest` z `TEST_DATABASE_URL` na bazo `glass_test`.
- V `frontend` poženi `npm run lint` in `npm test`.
- V brskalniku, ko tečeta API in Vite: natakar označi prihod, vidi status in zaključi; gost na Moje rezervacije vidi »gost je prišel« brez Odpovej; nova rezervacija iste mize istega dne pred zaključkom ne uspe in po zaključku uspe.

**Končano, ko:** ukazi in brskalnik pokrijejo sprejemne kriterije 1–10.
