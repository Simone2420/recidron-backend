# Recidron Backend

A FastAPI-based backend application with support for MySQL and PostgreSQL databases.

## Tech Stack

- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (0.24.0) - ASGI server for running FastAPI applications
- **SQLAlchemy** (2.0.23) - SQL toolkit and ORM
- **Alembic** (1.12.1) - Database migration tool
- **Pydantic** (2.5.2) - Data validation using Python type annotations
- **MySQL Connector** (8.2.0) - MySQL database driver
- **psycopg2** (2.9.9) - PostgreSQL database driver

## Project Structure

```
recidron-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection setup
│   ├── models/           # SQLAlchemy models (modular)
│   │   ├── __init__.py
│   │   └── item.py
│   ├── schemas/          # Pydantic schemas (modular)
│   │   ├── __init__.py
│   │   └── item.py
│   ├── routes/           # API routes/endpoints (modular)
│   │   ├── __init__.py
│   │   └── item.py
│   ├── services/         # Business logic (modular)
│   │   ├── __init__.py
│   │   └── item.py
│   └── middlewares/      # Custom middlewares
│       ├── __init__.py
│       └── timer.py
├── alembic/             # Database migrations
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md
```

## Prerequisites

- Python 3.10+
- MySQL 8.0+ (primary database)
- PostgreSQL 14+ (alternative database)

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
   ALTERNATE_DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   SECRET_KEY=your-secret-key
   DEBUG=False
   ```

   > **Note**: The application currently uses PostgreSQL (`ALTERNATE_DATABASE_URL`). To switch to MySQL, update both `app/database.py` and `alembic/env.py` to use `DATABASE_URL` instead.

## Database Setup

### Option 1: PostgreSQL (Current Default)

1. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE recidron;
   ```

2. **Run migrations**
   Alembic uses `ALTERNATE_DATABASE_URL` from `.env`:
   ```bash
   alembic upgrade head
   ```

### Option 2: MySQL

1. **Create MySQL database**
   ```sql
   CREATE DATABASE recidron;
   ```

2. **Update database configuration**
   Change the database URL in two files:
   - `app/database.py`: Replace `ALTERNATE_DATABASE_URL` with `DATABASE_URL`
   - `alembic/env.py`: Uncomment `DATABASE_URL` and comment `ALTERNATE_DATABASE_URL` in the `get_database_url()` function

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

### Creating Migrations

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Seed de permisos y roles

Para inicializar permisos y roles de seguridad (sin duplicados):

```bash
python -m app.scripts.seed_security
```

Para asignar rol `admin` a un usuario ya registrado:

```bash
python -m app.scripts.seed_security --admin-username TU_USUARIO
```

Opcional, para marcar además ese usuario como superusuario:

```bash
python -m app.scripts.seed_security --admin-username TU_USUARIO --make-superuser
```

## Running the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs


## API Endpoints

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/items/` | List all items (paginated) |
| GET | `/items/{id}` | Get item by ID |
| POST | `/items/` | Create new item |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

## Development

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