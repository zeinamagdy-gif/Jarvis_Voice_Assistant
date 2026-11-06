import sqlite3
from core import DATA_DIR
from . import skill, after

DB = DATA_DIR / "jarvis.db"


def _conn():
    conn = sqlite3.connect(DB)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER DEFAULT 0)"
    )
    return conn


@skill("add task", "add a task")
def add_task(text):
    title = after(text, "add a task", "add task")
    if not title:
        return "What is the task?"
    with _conn() as c:
        c.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    return f"Added task: {title}"


@skill("list tasks", "my tasks", "what are my tasks")
def list_tasks(text):
    with _conn() as c:
        rows = c.execute("SELECT id, title FROM tasks WHERE done = 0").fetchall()
    if not rows:
        return "You have no open tasks."
    return "Your tasks: " + ". ".join(f"{i}: {t}" for i, t in rows)


@skill("complete task", "finish task")
def complete_task(text):
    num = after(text, "complete task", "finish task")
    if not num.isdigit():
        return "Say complete task, then the number."
    with _conn() as c:
        cur = c.execute("UPDATE tasks SET done = 1 WHERE id = ?", (int(num),))
    return "Done." if cur.rowcount else "I couldn't find that task."
