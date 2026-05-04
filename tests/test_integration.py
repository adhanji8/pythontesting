"""
Integration tests for app.py

These tests exercise the full HTTP layer: routes, redirects, and rendered HTML.
The key technique is the application factory pattern — create_app() accepts a
store argument so each test gets its own isolated store, preventing state leakage
between tests.

The store fixture is exposed separately so tests can inspect it directly after
making HTTP requests (e.g. verifying a todo was actually deleted).
"""

import pytest
from todo.app import create_app
from todo.models import TodoStore


@pytest.fixture
def store():
    return TodoStore()


@pytest.fixture
def client(store):
    app = create_app(store)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ------------------------------------------------------------------ GET /


class TestIndex:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_shows_empty_message_when_no_todos(self, client):
        response = client.get("/")
        assert b"No todos yet" in response.data

    def test_renders_existing_todos(self, client, store):
        store.add("Buy milk")
        response = client.get("/")
        assert b"Buy milk" in response.data


# ----------------------------------------------------------------- POST /add


class TestAdd:
    def test_redirects_to_index_after_add(self, client):
        response = client.post("/add", data={"title": "Buy milk"})
        assert response.status_code == 302
        assert response.location == "/"

    def test_todo_appears_on_index_after_add(self, client):
        client.post("/add", data={"title": "Buy milk"})
        response = client.get("/")
        assert b"Buy milk" in response.data

    def test_empty_title_does_not_create_todo(self, client, store):
        client.post("/add", data={"title": ""})
        assert len(store.get_all()) == 0

    def test_whitespace_only_title_does_not_create_todo(self, client, store):
        client.post("/add", data={"title": "   "})
        assert len(store.get_all()) == 0

    def test_multiple_adds_are_all_present(self, client, store):
        client.post("/add", data={"title": "A"})
        client.post("/add", data={"title": "B"})
        assert len(store.get_all()) == 2


# --------------------------------------------------------------- POST /toggle


class TestToggle:
    def test_redirects_to_index(self, client, store):
        todo = store.add("Buy milk")
        response = client.post(f"/toggle/{todo.id}")
        assert response.status_code == 302
        assert response.location == "/"

    def test_marks_todo_as_complete(self, client, store):
        todo = store.add("Buy milk")
        client.post(f"/toggle/{todo.id}")
        assert store.get_by_id(todo.id).completed is True

    def test_toggle_twice_restores_incomplete(self, client, store):
        todo = store.add("Buy milk")
        client.post(f"/toggle/{todo.id}")
        client.post(f"/toggle/{todo.id}")
        assert store.get_by_id(todo.id).completed is False

    def test_unknown_id_still_redirects(self, client):
        response = client.post("/toggle/no-such-id")
        assert response.status_code == 302


# --------------------------------------------------------------- POST /delete


class TestDelete:
    def test_redirects_to_index(self, client, store):
        todo = store.add("Buy milk")
        response = client.post(f"/delete/{todo.id}")
        assert response.status_code == 302
        assert response.location == "/"

    def test_removes_todo_from_store(self, client, store):
        todo = store.add("Buy milk")
        client.post(f"/delete/{todo.id}")
        assert store.get_by_id(todo.id) is None

    def test_todo_no_longer_appears_on_index(self, client, store):
        todo = store.add("Buy milk")
        client.post(f"/delete/{todo.id}")
        response = client.get("/")
        assert b"Buy milk" not in response.data

    def test_unknown_id_still_redirects(self, client):
        response = client.post("/delete/no-such-id")
        assert response.status_code == 302
