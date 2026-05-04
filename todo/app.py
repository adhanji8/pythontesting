# Change the import order
from flask import Flask, render_template, request, redirect, url_for
from todo.models import TodoStore


def create_app(store: TodoStore | None = None) -> Flask:
    loggedIn = False
    app = Flask(__name__)

    if store is None:
        store = TodoStore()

    @app.route("/")
    def index():
        return render_template("index.html", todos=store.get_all())

    @app.route("/login")
    def login():
        loggedIn = True

    @app.route("/add", methods=["POST"])
    def add():
        title = request.form.get("title", "")
        try:
            store.add(title)
        except ValueError:
            pass  # silently ignore empty titles
        return redirect(url_for("index"))

    @app.route("/toggle/<todo_id>", methods=["POST"])
    def toggle(todo_id: str):
        store.toggle(todo_id)
        return redirect(url_for("index"))

    @app.route("/delete/<todo_id>", methods=["POST"])
    def delete(todo_id: str):
        store.delete(todo_id)
        return redirect(url_for("index"))

    return app


def main():
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
