from tests.conftest import glava, token

TERMIN = "2026-12-01T10:00:00"
DRUGI = "2026-12-01T18:00:00"


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
