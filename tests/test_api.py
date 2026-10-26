import os
import uuid

# Must be set before importing the app: use a throwaway SQLite file, not the real database.
os.environ["DATABASE_URL"] = "sqlite:///./test_ci.db"
os.environ.setdefault("SECRET_KEY", "test-secret-not-for-production")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

# Build the schema the same way production does: by running the migrations.
ALEMBIC_CFG = Config("alembic.ini")
command.upgrade(ALEMBIC_CFG, "head")

import main

client = TestClient(main.app)
EMAIL = f"user_{uuid.uuid4().hex[:8]}@example.com"
PASSWORD = "S3cure-pass-123"


@pytest.fixture(scope="module")
def token():
    r = client.post("/signup", json={"name": "Test User", "email": EMAIL, "password": PASSWORD, "skills": "python"})
    assert r.status_code == 200, r.text
    r = client.post("/login", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert "live" in r.json()["message"]


def test_wrong_password_rejected(token):
    r = client.post("/login", json={"email": EMAIL, "password": "wrong-password"})
    assert r.status_code == 401


def test_me_returns_logged_in_user(token):
    r = client.get("/me", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["logged_in_as"] == EMAIL


def test_create_posting_requires_login():
    r = client.post("/postings", json={"company_name": "Acme", "role_title": "Intern"})
    assert r.status_code in (401, 403)


def test_create_and_list_posting(token):
    r = client.post("/postings", headers=auth(token),
                    json={"company_name": "Acme", "role_title": "Backend Intern", "required_skills": "python, sql"})
    assert r.status_code == 200, r.text
    new_id = r.json()["id"]
    listed = client.get("/postings").json()
    assert any(p["id"] == new_id for p in listed)


def test_apply_to_missing_posting_404(token):
    r = client.post("/applications", headers=auth(token), json={"posting_id": 999999})
    assert r.status_code == 404


def test_postings_pagination_and_search(token):
    for i in range(3):
        client.post("/postings", headers=auth(token),
                    json={"company_name": f"PageCo{i}", "role_title": "Data Analyst", "required_skills": "excel, tableau"})
    client.post("/postings", headers=auth(token),
                json={"company_name": "100% Real_Co", "role_title": "Rust Engineer", "required_skills": "rust"})

    assert len(client.get("/postings?limit=2").json()) == 2
    page1 = client.get("/postings?limit=2&offset=0").json()
    page2 = client.get("/postings?limit=2&offset=2").json()
    assert {p["id"] for p in page1}.isdisjoint({p["id"] for p in page2})

    assert all("analyst" in p["role_title"].lower() for p in client.get("/postings?q=analyst").json())
    assert len(client.get("/postings?skill=tableau").json()) >= 3
    # wildcard characters are matched literally, not as patterns
    assert client.get("/postings?q=%25").json()[0]["company_name"] == "100% Real_Co"
    assert client.get("/postings?q=zzzz-no-match").json() == []


def test_postings_rejects_bad_paging():
    assert client.get("/postings?limit=0").status_code == 422
    assert client.get("/postings?limit=1000").status_code == 422
    assert client.get("/postings?offset=-1").status_code == 422


def test_migrations_match_models():
    """Fails if someone changes models.py without writing a migration."""
    command.check(ALEMBIC_CFG)
