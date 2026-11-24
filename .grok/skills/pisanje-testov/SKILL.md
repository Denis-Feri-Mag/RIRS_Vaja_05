---
name: pisanje-testov
description: Pisati ali dopolniti teste po konvencijah tega projekta, pytest za backend in Vitest za frontend. Uporabi, ko dodajaš teste za novo pot, stran ali popravek, ali ko preverjaš sprejemne kriterije.
---

# Pisanje testov

Testi naj preverijo sprejemne kriterije, ne notranjih podrobnosti. Pred zagonom preberi `AGENTS.md`.

## Backend, pytest

Datoteke so v `backend/tests/test_*.py`. Skupne stvari so v `conftest.py`:

- fikstura `app` vsakič ponovno ustvari shemo
- fikstura `client` je Flask test client
- fikstura `podatki` doda jedi, mizo in uporabnike (gost, natakar, kuhar, administrator), vsi imajo geslo `geslo`
- `token(client, email)` vrne JWT, `glava(zeton)` pa glavo `Authorization`

Vzorec, kot v `test_rezervacije.py`:

```
def test_ustvari_rezervacijo(client, podatki):
    zeton = token(client, "gost@test.com")
    odgovor = client.post("/api/rezervacije", headers=glava(zeton), json={...})
    assert odgovor.status_code == 201
    assert odgovor.get_json()["status"] == "potrjena"
```

Pokrij tudi zavrnjene primere: napačna vloga (403), manjkajoč zapis (404), napačno stanje (400), konflikt (409). Imena testov so v slovenščini, brez šumnikov, npr. `test_rezervacija_konflikt_in_odpoved`.

Zagon v mapi `backend`:

```
pytest
```

Potreben je `TEST_DATABASE_URL` na bazo `glass_test`.

## Frontend, Vitest

Testi stojijo ob izvorni datoteki, npr. `Prijava.test.jsx` in `api.test.js`. Uporabi Testing Library in `userEvent`. `fetch` nadomesti z `vi.stubGlobal("fetch", ...)`. V `afterEach` pokliči `vi.unstubAllGlobals()`.

Vzorec, kot v `Prijava.test.jsx`:

```
it("prikaze obrazec in ob uspesni prijavi shrani sejo", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({ token: "abc", vloga: "gost" }),
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<Prijava />);
  ...
});
```

Imena testov so v slovenščini, brez šumnikov. Zagon v mapi `frontend`:

```
npm test
```

Ne dodajaj novih testnih knjižnic, če obstoječi sklad zadošča.
