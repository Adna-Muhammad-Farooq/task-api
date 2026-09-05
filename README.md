# Task API

This is a simple Task API that I created using Python and FastAPI.

The purpose of this project is to practice building a REST API and understand how CRUD operations work.

## What this API can do

With this API, we can:

* Create a new task
* See all tasks
* See one task by its ID
* Update a task
* Delete a task
* Check if the API is working
* Test the API using Swagger UI

## Technologies I used

* Python
* FastAPI
* Uvicorn
* Pydantic

## How to run the project

First, install the required packages:

```bash
pip install fastapi uvicorn
```

Then start the server:

```bash
python -m uvicorn main:app --reload
```

After starting the server, open:

`http://127.0.0.1:8000`

To test the API using Swagger:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint      | What it does                          |
| ------ | ------------- | ------------------------------------- |
| GET    | `/`           | Shows basic information about the API |
| GET    | `/health`     | Checks if the API is working          |
| GET    | `/tasks`      | Shows all tasks                       |
| GET    | `/tasks/{id}` | Shows one task                        |
| POST   | `/tasks`      | Creates a new task                    |
| PUT    | `/tasks/{id}` | Updates a task                        |
| DELETE | `/tasks/{id}` | Deletes a task                        |

## Example Task

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false
}
```

## Testing

I tested the API using the Swagger UI available at `/docs`.

I tested the main CRUD operations:

* Creating a task
* Getting tasks
* Updating a task
* Deleting a task
* Testing invalid task IDs

## Storage

For this assignment, I used an in-memory Python list to store the tasks.

No database is used in this project.
