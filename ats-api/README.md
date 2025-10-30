# Headless, API-First Applicant Tracking System (ATS)

This project is a comprehensive, multi-tenant Applicant Tracking System (ATS) built with a headless, API-first architecture. It is designed to serve as the central hub in a modern recruitment ecosystem, providing a flexible and scalable backend for managing jobs, candidates, applications, and the entire hiring workflow.

The API is built using Python, FastAPI, and SQLAlchemy, with a PostgreSQL database for data persistence.

## Features

- **Multi-Tenant Architecture:** Securely isolates data between different client companies.
- **JWT Authentication:** Protects API endpoints using JSON Web Tokens.
- **Comprehensive API:** Provides full CRUD functionality for all core entities:
    - Jobs
    - Candidates
    - Applications
    - Resumes (with file uploads)
    - Interviews & Evaluations
- **Workflow Management:** Includes auditable event histories for job and application status changes.
- **Automatic API Documentation:** Interactive API documentation is available via Swagger UI at the `/docs` endpoint.

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd ats-api
    ```

2.  **Create a Virtual Environment:**
    It is highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install all required packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The application uses a `.env` file to manage environment variables.

1.  **Create the `.env` File:**
    Create a copy of the example environment file.
    ```bash
    cp .env.example .env
    ```

2.  **Configure Environment Variables:**
    Open the `.env` file and set the following variables:

    - `DATABASE_URL`: The connection string for your PostgreSQL database.
      *Example: `postgresql://user:password@localhost/ats_db`*

    - `SECRET_KEY`: A secret key used for signing JWTs. You can generate a secure key with the following command:
      ```bash
      openssl rand -hex 32
      ```

    - `ALGORITHM`: The algorithm used for JWT signing (default is `HS256`).
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: The lifetime of an access token in minutes (default is `30`).

### Running the Application

Once you have completed the installation and configuration, you can run the local development server.

1.  **Start the Server:**
    From the repository root (`ats-api/`), run the following command:
    ```bash
    uvicorn app.main:app --reload
    ```
    The `--reload` flag enables hot-reloading, so the server will automatically restart when you make code changes.

2.  **Access the API:**
    The API will be available at `http://127.0.0.1:8000`.

3.  **View the Documentation:**
    To explore the interactive API documentation, navigate to:
    `http://127.0.0.1:8000/docs`

## Testing

The project includes a comprehensive test suite to ensure code quality and correctness.

1.  **Run the Tests:**
    From the repository root, run the following command:
    ```bash
    PYTHONPATH=. python3 -m pytest
    ```
    This command ensures that the test runner can correctly locate the application modules. The tests use a separate, in-memory SQLite database to ensure they are isolated and do not affect your development database.
