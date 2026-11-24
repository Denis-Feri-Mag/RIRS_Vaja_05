from app import db
from app.models import Jed, Transakcija
from tests.conftest import glava, token


def _zasedi_in_odpri(client, miza_id, zeton):
    zasedba = client.post(f"/api/narocila/mize/{miza_id}/zasedi", headers=glava(zeton))
    assert zasedba.status_code == 200
    odprto = client.post("/api/narocila", headers=glava(zeton), json={"miza_id": miza_id})
    assert odprto.status_code == 201, odprto.get_json()
    return odprto.get_json()


def test_odpri_narocilo_in_pravilo_enega_odprtega(client, podatki):
    zeton = token(client, "natakar@test.com")
    miza_id = podatki["miza_id"]

    prosta = client.post("/api/narocila", headers=glava(zeton), json={"miza_id": miza_id})
    assert prosta.status_code == 400

    prvo = _zasedi_in_odpri(client, miza_id, zeton)
    assert prvo["status"] == "odprto"
    assert prvo["rezervacija_id"] is None

    drugo = client.post("/api/narocila", headers=glava(zeton), json={"miza_id": miza_id})
    assert drugo.status_code == 409


def test_dodaj_postavko(client, podatki):
    zeton = token(client, "natakar@test.com")
    narocilo = _zasedi_in_odpri(client, podatki["miza_id"], zeton)
    odgovor = client.post(
        f"/api/narocila/{narocilo['id']}/postavke",
        headers=glava(zeton),
        json={"jed_id": podatki["juha_id"], "kolicina": 2},
    )
    assert odgovor.status_code == 201
    telo = odgovor.get_json()
    assert telo["status"] == "caka"
    assert telo["cena"].startswith("8.5")
    assert telo["kolicina"] == 2


def test_kuhinja_vidi_samo_kuhinjske_jedi(client, podatki):
    natakar = token(client, "natakar@test.com")
    kuhar = token(client, "kuhar@test.com")
    narocilo = _zasedi_in_odpri(client, podatki["miza_id"], natakar)
    assert (
        client.post(
            f"/api/narocila/{narocilo['id']}/postavke",
            headers=glava(natakar),
            json={"jed_id": podatki["juha_id"], "kolicina": 1},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/api/narocila/{narocilo['id']}/postavke",
            headers=glava(natakar),
            json={"jed_id": podatki["voda_id"], "kolicina": 1},
        ).status_code
        == 201
    )

    pregled = client.get("/api/kuhinja", headers=glava(kuhar))
    assert pregled.status_code == 200
    jedi = [jed["naziv"] for skupina in pregled.get_json() for jed in skupina["jedi"]]
    assert "Gobova juha" in jedi
    assert "Mineralna voda" not in jedi


def test_tok_statusov(client, podatki):
    natakar = token(client, "natakar@test.com")
    kuhar = token(client, "kuhar@test.com")
    narocilo = _zasedi_in_odpri(client, podatki["miza_id"], natakar)
    juha = client.post(
        f"/api/narocila/{narocilo['id']}/postavke",
        headers=glava(natakar),
        json={"jed_id": podatki["juha_id"], "kolicina": 1},
    ).get_json()
    voda = client.post(
        f"/api/narocila/{narocilo['id']}/postavke",
        headers=glava(natakar),
        json={"jed_id": podatki["voda_id"], "kolicina": 1},
    ).get_json()

    def patch(zeton, postavka_id, status):
        return client.patch(
            f"/api/narocila/{narocilo['id']}/postavke/{postavka_id}",
            headers=glava(zeton),
            json={"status": status},
        )

    # kitchen item still waiting: waiter cannot mark it served, cook cannot mark it served
    assert patch(natakar, juha["id"], "postrezena").status_code == 400
    assert patch(kuhar, juha["id"], "postrezena").status_code == 403
    assert patch(natakar, juha["id"], "pripravljena").status_code == 403

    priprava = patch(kuhar, juha["id"], "pripravljena")
    assert priprava.status_code == 200
    assert priprava.get_json()["status"] == "pripravljena"
    assert patch(kuhar, juha["id"], "postrezena").status_code == 403

    postrezena = patch(natakar, juha["id"], "postrezena")
    assert postrezena.status_code == 200
    assert postrezena.get_json()["status"] == "postrezena"

    # a drink can be served by the waiter without the kitchen
    pijaca = patch(natakar, voda["id"], "postrezena")
    assert pijaca.status_code == 200
    assert pijaca.get_json()["status"] == "postrezena"


def test_zakljucek_narocila(client, app, podatki):
    natakar = token(client, "natakar@test.com")
    narocilo = _zasedi_in_odpri(client, podatki["miza_id"], natakar)
    assert (
        client.post(
            f"/api/narocila/{narocilo['id']}/postavke",
            headers=glava(natakar),
            json={"jed_id": podatki["juha_id"], "kolicina": 2},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/api/narocila/{narocilo['id']}/postavke",
            headers=glava(natakar),
            json={"jed_id": podatki["voda_id"], "kolicina": 1},
        ).status_code
        == 201
    )

    zakljucek = client.post(
        f"/api/narocila/{narocilo['id']}/zakljucek",
        headers=glava(natakar),
    )
    assert zakljucek.status_code == 200
    telo = zakljucek.get_json()
    assert telo["status"] == "zakljuceno"
    assert telo["miza_status"] == "prosta"
    assert telo["skupni_znesek"].startswith("19.5")

    with app.app_context():
        transakcije = db.session.scalars(
            db.select(Transakcija).filter_by(vrsta="prodaja", narocilo_id=narocilo["id"])
        ).all()
        assert len(transakcije) == 1
        assert str(transakcije[0].znesek).startswith("19.5")
        juha = db.session.get(Jed, podatki["juha_id"])
        voda = db.session.get(Jed, podatki["voda_id"])
        assert juha.zaloga == podatki["juha_zaloga"] - 2
        assert voda.zaloga == podatki["voda_zaloga"] - 1
