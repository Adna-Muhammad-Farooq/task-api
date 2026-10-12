
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from service import TaskService

app = FastAPI(title="Task API", version="1.0")

task_service = TaskService()


# Request models
class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": message},
    )


@app.get("/", summary="Get API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    return task_service.get_all_tasks()


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = task_service.get_task(task_id)

    if task is None:
        return error_response(f"Task {task_id} not found", 404)

    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        return error_response("Title cannot be empty", 400)

    return task_service.create_task(task.title)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        return error_response("Request body cannot be empty", 400)

    if (
        task_update.title is not None
        and not task_update.title.strip()
    ):
        return error_response("Title cannot be empty", 400)

    existing = task_service.get_task(task_id)

    if existing is None:
        return error_response(f"Task {task_id} not found", 404)

    updated_task = task_service.update_task(
        task_id,
        title=task_update.title,
        done=task_update.done,
    )

    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
)
def delete_task(task_id: int):
    deleted = task_service.delete_task(task_id)

    if not deleted:
        return error_response(f"Task {task_id} not found", 404)

    return Response(status_code=204)
