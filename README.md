# Task API — FastAPI, PostgreSQL & Docker

A RESTful CRUD API built with **FastAPI** and **PostgreSQL**, containerized using Docker and Docker Compose.

This project extends the original Task API from Assignment 2. It replaces SQLite storage with PostgreSQL and introduces separate repository and service layers to organize database operations and business logic.

## Features

- Create, retrieve, update, and delete tasks.
- PostgreSQL database running in Docker.
- Persistent database volume.
- Environment-based database configuration.
- Database table initialization using an SQL file.
- Separate repository and service layers.
- Interactive API documentation through Swagger UI.
- Start the application and database together using Docker Compose.

## Project Structure

```text
task-api/
├── main.py
├── service.py
├── repository.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── sql/
│   └── init.sql
└── README.md
```

## Architecture

The application separates HTTP handling, service operations, and database access.

- **main.py:** Defines FastAPI routes, validates request data, and returns HTTP responses.
- **service.py:** Coordinates task operations between the routes and repository.
- **repository.py:** Executes PostgreSQL queries for creating, retrieving, updating, and deleting tasks.
- **sql/init.sql:** Defines the PostgreSQL tasks table.
- **docker-compose.yml:** Starts the API and PostgreSQL containers together.

The original A2 implementation accessed SQLite directly from its route handlers. For A3, the code was refactored to introduce repository and service layers while preserving the existing endpoint URLs and response behavior.

## Technologies

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- Psycopg
- SQL
- Docker
- Docker Compose
- Pydantic

## Prerequisites

Install Docker Desktop and ensure its Docker engine is running.

## Environment Configuration

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local database credentials. The example file uses placeholder credentials and should not contain real secrets.

The application reads its database connection string from the `DATABASE_URL` environment variable.

The `.env` file is excluded from Git through `.gitignore`. Never commit real database credentials to GitHub.

## Run the Application

Build the application image and start the complete stack:

```powershell
docker compose up --build -d
```

Check the container status:

```powershell
docker compose ps
```

View application logs if needed:

```powershell
docker compose logs app
```

The API runs at:

http://localhost:8000

Swagger UI is available at:

http://localhost:8000/docs

The health endpoint is:

http://localhost:8000/health

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Get API information |
| GET | `/health` | Check API health |
| GET | `/tasks` | Retrieve all tasks |
| GET | `/tasks/{task_id}` | Retrieve one task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Example: Create a Task

Request:

```json
{
  "title": "Complete Assignment 3"
}
```

Send this request to `POST /tasks`. A successful creation returns status `201 Created` and the created task.

## Database

PostgreSQL runs in its own Docker container. The `tasks` table is initialized using `sql/init.sql`.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Primary key |
| `title` | TEXT | Task title |
| `done` | BOOLEAN | Task completion status |

The Compose configuration uses a named volume called `postgres_data` to preserve database files across container restarts and recreation.

The database is exposed on host port `5433`, while the application connects to PostgreSQL internally on port `5432`.

## Persistence Test

Persistence was tested by creating a task through the API:

```json
{
  "title": "Test Docker persistence"
}
```

The API returned `201 Created` with the task's ID and data.

Next, both containers were restarted using:

```powershell
docker compose restart
```

After restarting, the `/tasks` endpoint was checked again. The previously created task was still present, confirming that the PostgreSQL data survived the restart.

The named database volume is essential to this persistence behavior. Do not use `docker compose down -v` when you want to preserve the database volume.

## Useful Database Commands

List the tasks table:

```powershell
docker compose exec db psql -U taskuser -d taskdb -c "\dt"
```

View saved tasks:

```powershell
docker compose exec db psql -U taskuser -d taskdb -c "SELECT id, title, done FROM tasks ORDER BY id;"
```

## Stop the Application

Stop the containers without deleting the persistent database volume:

```powershell
docker compose down
```

Start the stack again:

```powershell
docker compose up -d
```

## Security

- Keep `.env` out of version control.
- Commit `.env.example` with placeholder credentials only.
- Use your own credentials when setting up a local copy of the project.
- Never publish database passwords or other secrets in screenshots, logs, or source


## AI Support Message Triage

This project includes an AI-powered support message classification feature using FastAPI and OpenRouter.

The `/triage` endpoint accepts a customer support message and returns:

- Category: billing, bug, feature, or other
- Urgency: low, normal, or high
- Confidence score
- Short explanation

### AI Evaluation Results

Evaluation date: October 29, 2026

Prompt version: triage_v1

Model route: openrouter/free

Total test cases: 8

- Category accuracy: 100% (8/8)
- Urgency accuracy: 75% (6/8)

The AI correctly classified all eight message categories.

However, it made two mistakes in urgency classification:

- Case 2: Expected high urgency, but AI returned normal.
- Case 8: Expected normal urgency, but AI returned low.

These results show that category classification performed well on this small test set, but urgency classification needs improvement.

To run the evaluation:

python evals/run_evals.py
