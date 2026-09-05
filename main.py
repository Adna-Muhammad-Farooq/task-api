from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0"
)


def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={"error": message}
    )


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test API with Swagger", "done": False}
]


# Stage 1

@app.get("/", summary="Get API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    return {
        "status": "ok"
    }


# Stage 2 - READ

@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    return error_response(
        f"Task {task_id} not found",
        404
    )


# Stage 3 - CREATE

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


# Stage 4 - UPDATE

@app.put(
    "/tasks/{task_id}",
    summary="Update a task"
)
def update_task(
    task_id: int,
    task_update: TaskUpdate
):

    for task in tasks:

        if task["id"] == task_id:

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

            if task_update.title is not None:
                task["title"] = task_update.title

            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    return error_response(
        f"Task {task_id} not found",
        404
    )


# Stage 4 - DELETE

@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task"
)
def delete_task(task_id: int):

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            tasks.pop(index)

            return Response(status_code=204)

    return error_response(
        f"Task {task_id} not found",
        404
    )