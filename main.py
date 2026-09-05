from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": message}
    )


class TaskCreate(BaseModel):
    title: str | None = None


tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test API with Swagger", "done": False}
]


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    return error_response(
        f"Task {task_id} not found",
        404
    )


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if not task.title or not task.title.strip():
        return error_response(
            "Title cannot be empty",
            400
        )

    new_id = max(
        [task["id"] for task in tasks],
        default=0
    ) + 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task