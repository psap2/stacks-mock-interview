def test_list_members(client):
    res = client.get("/api/members")
    assert res.status_code == 200
    assert len(res.get_json()) == 5


def test_get_member(client):
    assert client.get("/api/members/1").get_json()["name"] == "Priya Nair"
    assert client.get("/api/members/999").status_code == 404


def test_create_member(client):
    res = client.post("/api/members", json={"name": "Ada", "email": "ada@example.com"})
    assert res.status_code == 201
    assert client.get("/api/members/%d" % res.get_json()["id"]).status_code == 200


def test_create_member_rejects_bad_input(client):
    assert client.post("/api/members", json={"name": "Ada"}).status_code == 400
    assert client.post("/api/members", data="not json").status_code == 400
    dup = {"name": "Hana", "email": "hana@example.com"}
    assert client.post("/api/members", json=dup).status_code == 409


def test_list_books(client):
    res = client.get("/api/books")
    assert res.status_code == 200
    assert len(res.get_json()) == 7


def test_filter_books_by_author(client):
    res = client.get("/api/books?author=Ursula K. Le Guin")
    assert [b["year"] for b in res.get_json()] == [1969, 1968]


def test_list_loans(client):
    assert len(client.get("/api/loans").get_json()) == 6


def test_member_loans(client):
    assert len(client.get("/api/members/3/loans").get_json()) == 3
    assert client.get("/api/members/999/loans").status_code == 404
