import argparse
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parent / ".env")


def ensure_database():
    from app import database_url

    url = database_url()
    osnova, _, ime = url.rpartition("/")
    ime = ime.split("?", 1)[0]
    if "?" in url:
        query = "?" + url.rsplit("?", 1)[1]
    else:
        query = ""
    admin_url = f"{osnova}/postgres{query}"
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :ime"), {"ime": ime}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{ime}"'))
    engine.dispose()


def seed():
    from werkzeug.security import generate_password_hash

    from app import create_app, db
    from app.models import Jed, Miza, Skladisce, Uporabnik

    app = create_app()
    with app.app_context():
        db.create_all()
        db.session.execute(text("ALTER TABLE rezervacija DROP CONSTRAINT IF EXISTS ck_rezervacija_status"))
        db.session.execute(
            text(
                "ALTER TABLE rezervacija ADD CONSTRAINT ck_rezervacija_status "
                "CHECK (status IN ('potrjena', 'odpovedana', 'gost_prisel', 'zakljucena'))"
            )
        )
        db.session.commit()
        for naziv in ("kuhinja", "bar"):
            if db.session.query(Skladisce).filter_by(naziv=naziv).first() is None:
                db.session.add(Skladisce(naziv=naziv))
        db.session.commit()

        if db.session.query(Uporabnik).filter_by(email="admin@gmail.com").first() is None:
            db.session.add(
                Uporabnik(
                    ime="Admin",
                    priimek="Glass",
                    email="admin@gmail.com",
                    geslo_hash=generate_password_hash("admin"),
                    vloga="administrator",
                )
            )

        for stevilka, sedezi in ((1, 2), (2, 2), (3, 4), (4, 4), (5, 6)):
            if db.session.query(Miza).filter_by(stevilka=stevilka).first() is None:
                db.session.add(Miza(stevilka=stevilka, stevilo_sedezev=sedezi, status="prosta"))

        kuhinja = db.session.query(Skladisce).filter_by(naziv="kuhinja").one()
        bar = db.session.query(Skladisce).filter_by(naziv="bar").one()
        jedi = (
            ("Gobova juha", "predjed", "8.50", 20, kuhinja.id),
            ("Solata", "predjed", "7.00", 15, kuhinja.id),
            ("Goveja juha", "predjed", "6.50", 18, kuhinja.id),
            ("Zrezek", "glavna_jed", "16.00", 12, kuhinja.id),
            ("Rižota", "glavna_jed", "14.00", 14, kuhinja.id),
            ("Ribja plošča", "glavna_jed", "18.50", 10, kuhinja.id),
            ("Potica", "sladica", "5.50", 16, kuhinja.id),
            ("Sladoled", "sladica", "4.50", 20, kuhinja.id),
            ("Čaša vina", "pijaca", "3.50", 30, bar.id),
            ("Mineralna voda", "pijaca", "2.50", 40, bar.id),
        )
        for naziv, kategorija, cena, zaloga, skladisce_id in jedi:
            if db.session.query(Jed).filter_by(naziv=naziv).first() is None:
                db.session.add(
                    Jed(
                        skladisce_id=skladisce_id,
                        naziv=naziv,
                        cena=cena,
                        kategorija=kategorija,
                        zaloga=zaloga,
                    )
                )
        db.session.commit()


def main(ustvari_bazo=True):
    if ustvari_bazo:
        ensure_database()
    seed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Ustvari tabele in zaseje podatke, brez CREATE DATABASE.",
    )
    args = parser.parse_args()
    main(ustvari_bazo=not args.seed)
