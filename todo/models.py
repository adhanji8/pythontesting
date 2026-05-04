from dataclasses import dataclass, field
import uuid


@dataclass
class Todo:
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completed: bool = False


class TodoStore:
    def __init__(self):
        self._todos: list[Todo] = []

    def get_all(self) -> list[Todo]:
        return list(self._todos)

    def get_by_id(self, todo_id: str) -> "Todo | None":
        return next((t for t in self._todos if t.id == todo_id), None)

    def add(self, title: str) -> Todo:
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        todo = Todo(title=title.strip())
        self._todos.append(todo)
        return todo

    def toggle(self, todo_id: str) -> "Todo | None":
        todo = self.get_by_id(todo_id)
        if todo:
            todo.completed = not todo.completed
        return todo

    def delete(self, todo_id: str) -> bool:
        before = len(self._todos)
        self._todos = [t for t in self._todos if t.id != todo_id]
        return len(self._todos) < before
