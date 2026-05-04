"""
🤖 Note from Armaan: These tests target the business logic layer (Todo and TodoStore) with no
HTTP or framework involvement. Each test is self-contained: a fresh store
is created in setup_method so tests never share state.
"""

import pytest
from todo.models import Todo, TodoStore


class TestTodo:
    def test_has_title(self):
        todo = Todo(title="Buy milk")
        assert todo.title == "Buy milk"

    def test_defaults_to_incomplete(self):
        todo = Todo(title="Buy milk")
        assert todo.completed is False

    def test_each_todo_has_unique_id(self):
        a = Todo(title="A")
        b = Todo(title="B")
        assert a.id != b.id


class TestTodoStore:
    def setup_method(self):
        """Runs before every test — gives each test a clean, empty store."""
        self.store = TodoStore()

    # ------------------------------------------------------------------ add

    def test_add_returns_todo(self):
        todo = self.store.add("Buy milk")
        assert todo.title == "Buy milk"

    def test_add_persists_todo(self):
        self.store.add("Buy milk")
        assert len(self.store.get_all()) == 1

    def test_add_strips_whitespace(self):
        todo = self.store.add("  Buy milk  ")
        assert todo.title == "Buy milk"

    def test_add_raises_on_empty_title(self):
        with pytest.raises(ValueError):
            self.store.add("")

    def test_add_raises_on_whitespace_only_title(self):
        with pytest.raises(ValueError):
            self.store.add("   ")

    def test_add_multiple_todos(self):
        self.store.add("A")
        self.store.add("B")
        assert len(self.store.get_all()) == 2

    # --------------------------------------------------------------- toggle

    def test_toggle_marks_todo_as_complete(self):
        todo = self.store.add("Buy milk")
        self.store.toggle(todo.id)
        result = self.store.get_by_id(todo.id)
        assert result is not None
        assert result.completed is True

    def test_toggle_marks_complete_todo_as_incomplete(self):
        todo = self.store.add("Buy milk")
        self.store.toggle(todo.id)
        self.store.toggle(todo.id)
        result = self.store.get_by_id(todo.id)
        assert result is not None
        assert result.completed is False

    def test_toggle_unknown_id_returns_none(self):
        result = self.store.toggle("no-such-id")
        assert result is None

    # --------------------------------------------------------------- delete

    def test_delete_removes_todo(self):
        todo = self.store.add("Buy milk")
        self.store.delete(todo.id)
        assert self.store.get_by_id(todo.id) is None

    def test_delete_returns_true_on_success(self):
        todo = self.store.add("Buy milk")
        assert self.store.delete(todo.id) is True

    def test_delete_returns_false_for_unknown_id(self):
        assert self.store.delete("no-such-id") is False

    def test_delete_only_removes_target(self):
        a = self.store.add("A")
        b = self.store.add("B")
        self.store.delete(a.id)
        result = self.store.get_by_id(b.id)
        assert result is not None

    # --------------------------------------------------------------- get_all

    def test_get_all_initially_empty(self):
        assert self.store.get_all() == []
