from tests.conftest import glava, token


def test_zaloge_po_vlogah(client, podatki):
    natakar = token(client, "natakar@test.com")
    kuhar = token(client, "kuhar@test.com")
    gost = token(client, "gost@test.com")
    admin = token(client, "admin@test.com")

    natakar_kuhinja = client.get("/api/zaloge/kuhinja", headers=glava(natakar))
    assert natakar_kuhinja.status_code == 200
    assert any(jed["id"] == podatki["juha_id"] for jed in natakar_kuhinja.get_json())

    natakar_bar = client.get("/api/zaloge/bar", headers=glava(natakar))
    assert natakar_bar.status_code == 200
    assert any(jed["id"] == podatki["voda_id"] for jed in natakar_bar.get_json())

    assert client.get("/api/zaloge/kuhinja", headers=glava(kuhar)).status_code == 200
    assert client.get("/api/zaloge/bar", headers=glava(kuhar)).status_code == 403
    assert client.get("/api/zaloge/kuhinja", headers=glava(gost)).status_code == 403

    ročno = client.patch(
        f"/api/zaloge/{podatki['juha_id']}",
        headers=glava(natakar),
        json={"zaloga": 99},
    )
    assert ročno.status_code == 403
    assert (
        client.patch(
            f"/api/zaloge/{podatki['juha_id']}",
            headers=glava(kuhar),
            json={"zaloga": 99},
        ).status_code
        == 403
    )

    adminov = client.patch(
        f"/api/zaloge/{podatki['juha_id']}",
        headers=glava(admin),
        json={"zaloga": 3},
    )
    assert adminov.status_code == 200
    assert adminov.get_json()["zaloga"] == 3
