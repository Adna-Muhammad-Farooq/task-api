
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from service import TaskService
import json
from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from pydantic import ValidationError

from triage_models import TriageRequest, TriageResult
from triage_service import classify_message


app = FastAPI(title="Task API", version="1.0")

@app.exception_handler(RequestValidationError)
async def handle_request_validation(request: Request, exc: RequestValidationError):
    if request.url.path != "/triage":
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    errors = exc.errors()
    location = errors[0].get("loc", ()) if errors else ()
    field = next(
        (str(part) for part in location if part not in ("body",)),
        "body",
    )

    return JSONResponse(
        status_code=400,
        content={"error": f"Invalid field: {field}"},
    )

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

@app.post(
    "/triage",
    response_model=TriageResult,
    summary="Classify a support message with AI",
)
async def triage(triage_request: TriageRequest):
    try:
        result = await run_in_threadpool(
            classify_message,
            triage_request.text,
        )
        return result

    except (ValidationError, ValueError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "AI output failed validation after one repair attempt"
            },
        )

    except Exception:
        return JSONResponse(
            status_code=502,
            content={
                "error": "AI classification service failed"
            },
        )