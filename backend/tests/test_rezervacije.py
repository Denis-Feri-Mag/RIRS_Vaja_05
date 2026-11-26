from app import db
from app.models import Miza
from tests.conftest import glava, token

TERMIN = "2026-12-01T10:00:00"
DRUGI = "2026-12-01T18:00:00"
NASLEDNJI_DAN = "2026-12-02T10:00:00"


def _rezervacija(client, zeton, miza_id, zacetek=TERMIN):
    odgovor = client.post(
        "/api/rezervacije",
        headers=glava(zeton),
        json={"zacetek": zacetek, "miza_id": miza_id, "stevilo_oseb": 2},
    )
    assert odgovor.status_code == 201, odgovor.get_json()
    return odgovor.get_json()


def _dodaj_mizo(app, stevilka):
    with app.app_context():
        miza = Miza(stevilka=stevilka, stevilo_sedezev=4, status="prosta")
        db.session.add(miza)
        db.session.commit()
        return miza.id


def test_ustvari_rezervacijo(client, podatki):
    zeton = token(client, "gost@test.com")
    odgovor = client.post(
        "/api/rezervacije",
        headers=glava(zeton),
        json={
            "zacetek": TERMIN,
            "miza_id": podatki["miza_id"],
            "stevilo_oseb": 2,
            "opomba": "Ob oknu",
        },
    )
    assert odgovor.status_code == 201
    telo = odgovor.get_json()
    assert telo["status"] == "potrjena"
    assert telo["opomba"] == "Ob oknu"
    assert telo["trajanje_minut"] == 120

    seznam = client.get("/api/rezervacije", headers=glava(zeton))
    assert seznam.status_code == 200
    assert len(seznam.get_json()) == 1
    assert seznam.get_json()[0]["id"] == telo["id"]


def test_rezervacija_konflikt_in_odpoved(client, podatki):
    prvi = token(client, "gost@test.com")
    drugi_gost = client.post(
        "/api/register",
        json={"ime": "Tina", "priimek": "Gost", "email": "tina@test.com", "geslo": "geslo"},
    )
    assert drugi_gost.status_code == 201
    drugi = drugi_gost.get_json()["token"]

    ustvarjena = client.post(
        "/api/rezervacije",
        headers=glava(prvi),
        json={"zacetek": TERMIN, "miza_id": podatki["miza_id"], "stevilo_oseb": 2},
    )
    assert ustvarjena.status_code == 201
    rezervacija_id = ustvarjena.get_json()["id"]

    konflikt = client.post(
        "/api/rezervacije",
        headers=glava(drugi),
        json={"zacetek": DRUGI, "miza_id": podatki["miza_id"], "stevilo_oseb": 2},
    )
    assert konflikt.status_code == 409
    assert "ni prosta" in konflikt.get_json()["napaka"]

    tuja = client.post(
        f"/api/rezervacije/{rezervacija_id}/odpoved",
        headers=glava(drugi),
    )
    assert tuja.status_code == 404

    odpoved = client.post(
        f"/api/rezervacije/{rezervacija_id}/odpoved",
        headers=glava(prvi),
    )
    assert odpoved.status_code == 200
    assert odpoved.get_json()["status"] == "odpovedana"

    nova = client.post(
        "/api/rezervacije",
        headers=glava(drugi),
        json={"zacetek": TERMIN, "miza_id": podatki["miza_id"], "stevilo_oseb": 2},
    )
    assert nova.status_code == 201


def test_prihod_gosta(client, podatki):
    gost = token(client, "gost@test.com")
    natakar = token(client, "natakar@test.com")
    kuhar = token(client, "kuhar@test.com")
    admin = token(client, "admin@test.com")
    rezervacija = _rezervacija(client, gost, podatki["miza_id"])
    pot = f"/api/rezervacije/{rezervacija['id']}/prihod"

    zavrnjen_gost = client.post(pot, headers=glava(gost))
    assert zavrnjen_gost.status_code == 403
    zavrnjen_kuhar = client.post(pot, headers=glava(kuhar))
    assert zavrnjen_kuhar.status_code == 403
    brez_zetona = client.post(pot)
    assert brez_zetona.status_code == 401

    prihod = client.post(pot, headers=glava(natakar))
    assert prihod.status_code == 200
    assert prihod.get_json()["status"] == "gost_prisel"

    ponovno = client.post(pot, headers=glava(natakar))
    assert ponovno.status_code == 400
    assert "potrjeni" in ponovno.get_json()["napaka"]

    ni_zapisa = client.post("/api/rezervacije/999999/prihod", headers=glava(natakar))
    assert ni_zapisa.status_code == 404

    druga = _rezervacija(client, gost, podatki["miza_id"], NASLEDNJI_DAN)
    admin_prihod = client.post(
        f"/api/rezervacije/{druga['id']}/prihod",
        headers=glava(admin),
    )
    assert admin_prihod.status_code == 200
    assert admin_prihod.get_json()["status"] == "gost_prisel"


def test_dan_vkljucuje_prispele(client, app, podatki):
    gost = token(client, "gost@test.com")
    natakar = token(client, "natakar@test.com")
    mize = [podatki["miza_id"], _dodaj_mizo(app, 2), _dodaj_mizo(app, 3), _dodaj_mizo(app, 4)]

    prisel = _rezervacija(client, gost, mize[0])
    potrjena = _rezervacija(client, gost, mize[1])
    odpovedana = _rezervacija(client, gost, mize[2])
    zakljucena = _rezervacija(client, gost, mize[3])

    assert client.post(
        f"/api/rezervacije/{prisel['id']}/prihod", headers=glava(natakar)
    ).status_code == 200
    assert client.post(
        f"/api/rezervacije/{odpovedana['id']}/odpoved", headers=glava(gost)
    ).status_code == 200
    assert client.post(
        f"/api/rezervacije/{zakljucena['id']}/zakljucek", headers=glava(natakar)
    ).status_code == 200

    dan = client.get("/api/rezervacije/dan?datum=2026-12-01", headers=glava(natakar))
    assert dan.status_code == 200
    po_id = {vrstica["id"]: vrstica for vrstica in dan.get_json()}
    assert set(po_id) == {prisel["id"], potrjena["id"]}
    assert po_id[prisel["id"]]["status"] == "gost_prisel"
    assert po_id[potrjena["id"]]["status"] == "potrjena"
    assert po_id[prisel["id"]]["ura"] == "10:00"


def test_prispela_rezervacija_drzi_mizo(client, podatki):
    gost = token(client, "gost@test.com")
    natakar = token(client, "natakar@test.com")
    rezervacija = _rezervacija(client, gost, podatki["miza_id"])
    pot = f"/api/rezervacije/{rezervacija['id']}"

    prihod = client.post(f"{pot}/prihod", headers=glava(natakar))
    assert prihod.status_code == 200

    konflikt = client.post(
        "/api/rezervacije",
        headers=glava(gost),
        json={"zacetek": DRUGI, "miza_id": podatki["miza_id"], "stevilo_oseb": 2},
    )
    assert konflikt.status_code == 409
    assert "ni prosta" in konflikt.get_json()["napaka"]

    odpoved = client.post(f"{pot}/odpoved", headers=glava(gost))
    assert odpoved.status_code == 400
    seznam = client.get("/api/rezervacije", headers=glava(gost))
    assert seznam.get_json()[0]["status"] == "gost_prisel"

    zakljucek = client.post(f"{pot}/zakljucek", headers=glava(natakar))
    assert zakljucek.status_code == 200
    assert zakljucek.get_json()["status"] == "zakljucena"

    nova = client.post(
        "/api/rezervacije",
        headers=glava(gost),
        json={"zacetek": TERMIN, "miza_id": podatki["miza_id"], "stevilo_oseb": 2},
    )
    assert nova.status_code == 201
