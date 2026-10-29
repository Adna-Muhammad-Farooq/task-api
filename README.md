# Task API — FastAPI, PostgreSQL, Docker & AI Triage

A RESTful API built with **FastAPI**, **PostgreSQL**, and **Docker**, with an AI-powered support message classification feature using **OpenRouter**.

This project started as a task management API and was improved through different Backend AI Engineering assignments.

The application supports task CRUD operations, PostgreSQL database storage, Docker deployment, and AI-powered customer support message classification.

## Features

### Task Management
- Create, retrieve, update, and delete tasks.
- Store task data in PostgreSQL.
- Use Docker Compose to run the application and database.
- Preserve database records using a Docker volume.
- Organize database operations using repository and service layers.
- Access interactive API documentation through Swagger UI.

### AI Support Message Triage
- Classify customer support messages using an LLM through OpenRouter.
- Identify message categories: `billing`, `bug`, `feature`, or `other`.
- Identify urgency levels: `low`, `normal`, or `high`.
- Return a confidence score and short explanation.
- Validate AI responses using Pydantic.
- Attempt to repair invalid AI responses once.
- Retry requests after temporary AI service errors.
- Support environment-based AI configuration and a kill switch.
- Record AI request information and errors for debugging.
- Evaluate AI classification using a small test dataset.

## Project Structure

```text
task-api/
├── main.py
├── service.py
├── repository.py
├── triage_models.py
├── triage_client.py
├── triage_service.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── JOB-CARD.md
├── prompts/
│   └── triage_v1.txt
├── evals/
│   ├── cases.json
│   ├── run_evals.py
│   ├── test_repair.py
│   └── test_retry.py
├── sql/
│   └── init.sql
└── README.md
```

## Architecture

The project separates API handling, business logic, database operations, and AI processing.

- **main.py:** Defines FastAPI routes and returns HTTP responses.
- **service.py:** Handles task management business logic.
- **repository.py:** Executes PostgreSQL database queries.
- **triage_models.py:** Defines and validates AI triage data.
- **triage_client.py:** Configures the AI client.
- **triage_service.py:** Handles AI classification, validation, repair, retries, and logging.
- **prompts/triage_v1.txt:** Stores the versioned AI classification prompt.
- **evals/:** Contains evaluation data and automated AI tests.
- **sql/init.sql:** Defines the PostgreSQL tasks table.
- **docker-compose.yml:** Configures the application and PostgreSQL containers.

The original task management API used SQLite. It was later improved to use PostgreSQL with separate repository and service layers.

The AI triage feature was added without removing the existing task management functionality.

## Technologies

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- Psycopg
- SQL
- SQLAlchemy (if used in other project modules)
- Docker
- Docker Compose
- Pydantic
- OpenRouter API
- OpenAI Python SDK
- HTTPX
- Git and GitHub

## Prerequisites

Before running the project, install:

- Python
- Docker Desktop
- Git

For AI classification, you also need an OpenRouter API key.

## Environment Configuration

Create a local `.env` file using the example:

```powershell
Copy-Item .env.example .env
```

Update the local `.env` file with your database configuration and OpenRouter API key.

Example AI configuration:

```env
OPENROUTER_API_KEY=your_api_key_here
LLM_ENABLED=true
LLM_STUB=0
```

Use the exact environment variable names supported by your local application.

The `.env` file must not be uploaded to GitHub because it contains private credentials.

The `.env.example` file should contain placeholder values only.

## Installation

Open the project folder in VS Code.

Create a Python virtual environment:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application with Docker

Make sure Docker Desktop is running.

Build and start the application and PostgreSQL:

```powershell
docker compose up --build -d
```

Check container status:

```powershell
docker compose ps
```

View application logs:

```powershell
docker compose logs app
```

The API is available at:

http://localhost:8000

Swagger UI:

http://localhost:8000/docs

Health endpoint:

http://localhost:8000/health

## Run the API Locally

Make sure the required environment variables are configured and PostgreSQL is accessible.

Start FastAPI:

```powershell
uvicorn main:app --reload
```

Open Swagger UI:

http://127.0.0.1:8000/docs

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
| POST | `/triage` | Classify a customer support message using AI |

## Task Management Example

Send a POST request to `/tasks` with:

```json
{
  "title": "Complete Backend AI Engineering Assignment"
}
```

A successful request creates a task and returns HTTP `201 Created`.

## Database

PostgreSQL runs in a separate Docker container.

The `tasks` table is initialized using `sql/init.sql`.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Primary key |
| `title` | TEXT | Task title |
| `done` | BOOLEAN | Task completion status |

The application uses a named Docker volume called `postgres_data` to preserve database files.

PostgreSQL is exposed on host port `5433`, while the application communicates with PostgreSQL internally using port `5432`.

## Database Persistence Test

Database persistence was tested by creating a task through the API.

Example:

```json
{
  "title": "Test Docker persistence"
}
```

The API returned HTTP `201 Created`.

Both containers were then restarted:

```powershell
docker compose restart
```

After restarting, the task was still available through `/tasks`.

This confirmed that PostgreSQL data survived the container restart.

To preserve database records, do not remove the named volume.

## AI Support Message Triage

The `/triage` endpoint uses an LLM through OpenRouter to classify customer support messages.

The endpoint returns four main fields:

- **Category:** Type of customer issue.
- **Urgency:** Priority of the issue.
- **Confidence:** AI confidence score.
- **Reason:** Short explanation of the classification.

### Example Request

Send a POST request to `/triage`:

```json
{
  "text": "I was charged twice for my subscription."
}
```

### Example Response

An example of the expected response structure:

```json
{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.9,
  "reason": "The customer reports a duplicate payment."
}
```

The actual response may vary depending on the AI model.

## AI Prompt

The classification instructions are stored in:

```text
prompts/triage_v1.txt
```

The prompt contains instructions and examples to help the model classify messages.

The prompt version is:

`triage_v1`

Keeping the prompt in a separate file makes it easier to update and evaluate.

## AI Response Validation

The application uses Pydantic to validate AI output.

It checks that the model returns the required fields with valid values.

If the model returns an invalid response, the application makes one repair attempt.

If the response remains invalid, the application rejects it instead of returning incorrect data.

The API returns HTTP `422` when AI output cannot be validated after the repair attempt.

## AI Retry Handling

The application includes retry handling for temporary AI service problems.

For example, if the AI service returns HTTP `503`, the application can retry the request.

The retry logic includes waiting between attempts.

This helps the API handle temporary service errors more reliably.

## AI Error Handling and Logging

The application records information about AI requests and failures, including relevant details such as:

- Prompt version
- Model route
- Request duration
- Retry attempt
- Repair count
- Error information

The API does not expose raw invalid AI output to the client when validation fails.

Production logs should be protected because AI output may contain sensitive user information.

## AI Evaluation

The project includes eight test cases in:

```text
evals/cases.json
```

These cases check whether the AI correctly predicts message categories and urgency levels.

### Latest Evaluation Results

**Evaluation date:** October 29, 2026

**Prompt version:** `triage_v1`

**Model route:** `openrouter/free`

**Total test cases:** 8

| Metric | Correct | Accuracy |
|---|---|---|
| Category classification | 8/8 | 100% |
| Urgency classification | 4/8 | 50% |

The AI correctly identified all eight message categories.

However, it made four mistakes in urgency classification:

- **Case 2:** Expected high, but returned normal.
- **Case 5:** Expected low, but returned normal.
- **Case 6:** Expected low, but returned normal.
- **Case 8:** Expected normal, but returned low.

An earlier evaluation achieved 75% urgency accuracy, while the latest evaluation achieved 50%.

The results can vary because the application uses a live AI model.

These results show that category classification worked well on the small test dataset, but urgency classification still needs improvement.

Eight test cases are not enough to measure real-world performance reliably.

### Run the Evaluation

```powershell
python evals/run_evals.py
```

## Automated AI Tests

The project includes automated tests for AI response validation and error handling.

### 1. AI Repair and Validation Test

Run:

```powershell
python evals/test_repair.py
```

This test verifies:

- Invalid AI responses trigger a repair attempt.
- Valid repaired responses are accepted.
- Two invalid responses are rejected.
- The API returns HTTP `422` when AI output remains invalid.
- Raw invalid AI output is not included in the HTTP response.

**Test result:** Passed on October 29, 2026.

### 2. AI Retry Test

Run:

```powershell
python evals/test_retry.py
```

This test simulates a temporary HTTP `503` server error.

It verifies that the application retries and processes a successful response afterward.

Observed test results:

```text
Model calls: 2
Retry waits: 1
RETRY TEST PASSED
```

**Test result:** Passed on October 29, 2026.

## Useful Database Commands

List database tables:

```powershell
docker compose exec db psql -U taskuser -d taskdb -c "\dt"
```

View saved tasks:

```powershell
docker compose exec db psql -U taskuser -d taskdb -c "SELECT id, title, done FROM tasks ORDER BY id;"
```

## Stop the Application

Stop the containers without deleting the database volume:

```powershell
docker compose down
```

Start them again:

```powershell
docker compose up -d
```

Avoid using `docker compose down -v` if you want to preserve PostgreSQL data.

## Security

- Never commit `.env` or real API keys to GitHub.
- Use `.env.example` with placeholder credentials only.
- Keep database passwords private.
- Avoid publishing secrets in screenshots, logs, or source code.
- Validate AI output before returning it to users.
- Handle temporary AI service errors safely.
- Protect application logs from unauthorized access.

## Project Summary

This project demonstrates how a basic FastAPI CRUD application can be extended with database persistence, Docker deployment, and LLM integration.

The main learning outcomes include:

- Building REST APIs with FastAPI.
- Managing data with PostgreSQL.
- Running applications with Docker Compose.
- Separating API, service, and repository layers.
- Integrating an LLM through OpenRouter.
- Validating and repairing AI-generated responses.
- Handling temporary AI service failures.
- Evaluating AI classification results.
- Writing automated tests for AI-powered API behavior.

The project combines traditional backend development with practical AI engineering techniques.