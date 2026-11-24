from tests.conftest import glava, token


def test_health(client):
    odgovor = client.get("/health")
    assert odgovor.status_code == 200
    assert odgovor.get_json() == {"status": "ok"}


def test_database_url():
    from app import database_url

    assert (
        database_url("postgresql://u:p@host/neondb?sslmode=require")
        == "postgresql+psycopg://u:p@host/neondb?sslmode=require"
    )
    assert (
        database_url("postgres://u:p@host/neondb?sslmode=require")
        == "postgresql+psycopg://u:p@host/neondb?sslmode=require"
    )
    obstojeci = "postgresql+psycopg://u:p@host/neondb?sslmode=require"
    assert database_url(obstojeci) == obstojeci


def test_register_in_prijava(client):
    podatki = {
        "ime": "Ema",
        "priimek": "Novak",
        "email": "ema@test.com",
        "geslo": "skrivnost",
    }
    ustvarjen = client.post("/api/register", json=podatki)
    assert ustvarjen.status_code == 201
    telo = ustvarjen.get_json()
    assert telo["vloga"] == "gost"
    assert telo["ime"] == "Ema"
    assert "token" in telo

    prijava = client.post("/api/login", json={"email": "ema@test.com", "geslo": "skrivnost"})
    assert prijava.status_code == 200
    assert prijava.get_json()["vloga"] == "gost"

    napacna = client.post("/api/login", json={"email": "ema@test.com", "geslo": "narobe"})
    assert napacna.status_code == 401


def test_register_podvojen_email(client):
    podatki = {
        "ime": "Ema",
        "priimek": "Novak",
        "email": "ema@test.com",
        "geslo": "skrivnost",
    }
    assert client.post("/api/register", json=podatki).status_code == 201
    drugi = client.post("/api/register", json=podatki)
    assert drugi.status_code == 409
    assert "Email" in drugi.get_json()["napaka"]


def test_gost_nima_dostopa_do_natakarskih_poti(client, podatki):
    gost = token(client, "gost@test.com")
    natakar = token(client, "natakar@test.com")
    gostov = client.get("/api/narocila/mize", headers=glava(gost))
    assert gostov.status_code == 403
    natakarjev = client.get("/api/narocila/mize", headers=glava(natakar))
    assert natakarjev.status_code == 200
    assert any(miza["id"] == podatki["miza_id"] for miza in natakarjev.get_json())
