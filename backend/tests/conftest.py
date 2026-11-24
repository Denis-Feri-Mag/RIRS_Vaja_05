import os

import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash

os.environ.setdefault("JWT_SECRET", "test-secret-za-vajo-naj-bo-dovolj-dolg")
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL") or os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://box@127.0.0.1:5432/glass_test"
)

from app import create_app, db
from app.models import Jed, Miza, Skladisce, Uporabnik


@pytest.fixture()
def app():
    application = create_app()
    application.config["TESTING"] = True
    with application.app_context():
        db.session.execute(text("DROP SCHEMA public CASCADE"))
        db.session.execute(text("CREATE SCHEMA public"))
        db.session.commit()
        db.create_all()
        yield application
        db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def podatki(app):
    with app.app_context():
        kuhinja = Skladisce(naziv="kuhinja")
        bar = Skladisce(naziv="bar")
        db.session.add_all([kuhinja, bar])
        db.session.flush()

        juha = Jed(
            skladisce_id=kuhinja.id,
            naziv="Gobova juha",
            cena="8.50",
            kategorija="predjed",
            zaloga=10,
        )
        voda = Jed(
            skladisce_id=bar.id,
            naziv="Mineralna voda",
            cena="2.50",
            kategorija="pijaca",
            zaloga=20,
        )
        miza = Miza(stevilka=1, stevilo_sedezev=4, status="prosta")
        db.session.add_all([juha, voda, miza])

        osebe = [
            Uporabnik(
                ime="Ana",
                priimek="Gost",
                email="gost@test.com",
                geslo_hash=generate_password_hash("geslo"),
                vloga="gost",
            ),
            Uporabnik(
                ime="Bojan",
                priimek="Natakar",
                email="natakar@test.com",
                geslo_hash=generate_password_hash("geslo"),
                vloga="natakar",
            ),
            Uporabnik(
                ime="Cilka",
                priimek="Kuhar",
                email="kuhar@test.com",
                geslo_hash=generate_password_hash("geslo"),
                vloga="kuhar",
            ),
            Uporabnik(
                ime="Admin",
                priimek="Glass",
                email="admin@test.com",
                geslo_hash=generate_password_hash("geslo"),
                vloga="administrator",
            ),
        ]
        db.session.add_all(osebe)
        db.session.commit()
        return {
            "juha_id": juha.id,
            "voda_id": voda.id,
            "miza_id": miza.id,
            "juha_zaloga": juha.zaloga,
            "voda_zaloga": voda.zaloga,
        }


def token(client, email):
    odgovor = client.post("/api/login", json={"email": email, "geslo": "geslo"})
    assert odgovor.status_code == 200, odgovor.get_json()
    return odgovor.get_json()["token"]


def glava(zeton):
    return {"Authorization": f"Bearer {zeton}"}
