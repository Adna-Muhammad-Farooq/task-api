from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3


app = FastAPI(
    title="Task API",
    version="1.0"
)


# Database connection
def get_db():
    connection = sqlite3.connect("tasks.db")
    connection.row_factory = sqlite3.Row
    return connection


# Create database table and example tasks
def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    count = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if count == 0:
        connection.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Connect SQLite database", 0)
            ]
        )

    connection.commit()
    connection.close()


init_db()


# Request models
class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# Error response
def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": message}
    )


# Root
@app.get("/", summary="Get API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# Health
@app.get("/health", summary="Check API health")
def health():
    return {
        "status": "ok"
    }


# GET all tasks
@app.get("/tasks", summary="Get all tasks")
def get_tasks():

    connection = get_db()

    rows = connection.execute(
        "SELECT id, title, done FROM tasks ORDER BY id"
    ).fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]


# GET one task
@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):

    connection = get_db()

    row = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return error_response(
            f"Task {task_id} not found",
            404
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# POST create task
@app.post(
    "/tasks",
    status_code=201,
    summary="Create a new task"
)
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        return error_response(
            "Title cannot be empty",
            400
        )

    connection = get_db()

    cursor = connection.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )

    connection.commit()

    task_id = cursor.lastrowid

    row = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# PUT update task
@app.put(
    "/tasks/{task_id}",
    summary="Update a task"
)
def update_task(
    task_id: int,
    task_update: TaskUpdate
):

    if (
        task_update.title is None
        and task_update.done is None
    ):
        return error_response(
            "Request body cannot be empty",
            400
        )

    if (
        task_update.title is not None
        and not task_update.title.strip()
    ):
        return error_response(
            "Title cannot be empty",
            400
        )

    connection = get_db()

    existing = connection.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if existing is None:
        connection.close()

        return error_response(
            f"Task {task_id} not found",
            404
        )

    if task_update.title is not None:
        connection.execute(
            "UPDATE tasks SET title = ? WHERE id = ?",
            (task_update.title, task_id)
        )

    if task_update.done is not None:
        connection.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (int(task_update.done), task_id)
        )

    connection.commit()

    row = connection.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# DELETE task
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task"
)
def delete_task(task_id: int):

    connection = get_db()

    existing = connection.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if existing is None:
        connection.close()

        return error_response(
            f"Task {task_id} not found",
            404
        )

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return Response(status_code=204)