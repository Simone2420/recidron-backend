# Recidron Backend

A FastAPI-based backend application with MySQL database support.

## Tech Stack

- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (0.24.0) - ASGI server for running FastAPI applications
- **SQLAlchemy** (2.0.23) - SQL toolkit and ORM
- **Alembic** (1.12.1) - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **python-dotenv** - Environment variable management
- **MySQL Connector** (8.2.0) - MySQL database driver

## Project Structure

```
recidron-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Configuration settings
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routes/          # API routes/endpoints
│   └── services/        # Business logic
├── alembic/             # Database migrations
├── tests/               # Test files
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md
```

## Prerequisites

- Python 3.10+
- MySQL 8.0+

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recidron-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/dbname
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

## Database Setup

1. **Create MySQL database**
   ```sql
   CREATE DATABASE recidron;
   ```

2. **Run migrations**
   Alembic reads `DATABASE_URL` from `.env`.

   Verify the value is present before running migrations:
   ```powershell
   Get-Content .env | Select-String DATABASE_URL
   ```

   ```bash
   alembic upgrade head
   ```

3. **Create new migration (if needed)**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

## Running the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Linting
```bash
flake8 app/
mypy app/
```

## License

[MIT License](LICENSE)