# Recidron Backend

A FastAPI-based backend application with integrated security (JWT authentication, role-based access control) and support for MySQL and PostgreSQL databases.

## Tech Stack

- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (0.24.0) - ASGI server for running FastAPI applications
- **SQLAlchemy** (2.0.23) - SQL toolkit and ORM
- **Alembic** (1.12.1) - Database migration tool
- **Pydantic** (2.5.2) - Data validation using Python type annotations
- **python-jose** (3.3.0) - JWT token handling
- **passlib[argon2]** (1.7.4) - Password hashing with Argon2
- **argon2-cffi** (23.1.0) - Argon2 cryptography backend
- **MySQL Connector** (8.2.0) - MySQL database driver
- **psycopg2** (2.9.9) - PostgreSQL database driver

## Project Structure

```
recidron-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings (DB, JWT, etc)
│   ├── database.py          # Database connection setup
│   ├── core/                # Core utilities
│   │   ├── security.py      # JWT and password hashing (Argon2)
│   │   └── deps.py          # FastAPI dependencies (OAuth2, permissions)
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── item.py          # Item model
│   │   └── security.py      # Person, User, Role, Permission models
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── item.py          # Item schemas
│   │   └── security.py      # Security schemas (User, Role, Permission, Token)
│   ├── routes/              # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── item.py          # Item endpoints
│   │   └── auth.py          # Authentication & authorization endpoints
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── item.py          # Item service
│   │   └── security.py      # Security service (users, roles, auth)
│   ├── scripts/             # Utility scripts
│   │   ├── __init__.py
│   │   └── seed_security.py # Seed database with roles/permissions
│   └── middlewares/         # Custom middlewares
│       ├── __init__.py
│       └── timer.py         # Request timing middleware
├── alembic/                 # Database migrations
│   ├── versions/
│   │   ├── 90ea32905fbb_initial_schema.py
│   │   └── e3c1f4b2a9d0_add_security_module.py
│   ├── env.py
│   └── alembic.ini
├── .env                     # Environment variables
├── requirements.txt         # Project dependencies
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
   # Database (use one or both)
   DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/recidron
   ALTERNATE_DATABASE_URL=postgresql://user:password@localhost:5432/recidron
   
   # JWT Security
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # Application
   DEBUG=False
   ```

   > **Important**: 
   > - Change `SECRET_KEY` to a strong random value in production
   > - The app automatically uses `ALTERNATE_DATABASE_URL` if set, otherwise falls back to `DATABASE_URL`
   > - For development, you can generate a SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Database Setup

### Option 1: PostgreSQL (Default)

1. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE recidron;
   ```

2. **Configure environment** (in `.env`)
   ```env
   ALTERNATE_DATABASE_URL=postgresql://user:password@localhost:5432/recidron
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

### Option 2: MySQL

1. **Create MySQL database**
   ```sql
   CREATE DATABASE recidron;
   ```

2. **Configure environment** (in `.env`)
   ```env
   DATABASE_URL=mysql+mysqlconnector://user:password@localhost:3306/recidron
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

### Database Migrations

#### View migration status
```bash
alembic current
```

#### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Upgrade to latest migration
```bash
alembic upgrade head
```

#### Downgrade to previous migration
```bash
alembic downgrade -1
```

#### Downgrade to specific revision
```bash
alembic downgrade 90ea32905fbb   # Downgrade to initial schema only
```

#### View migration history
```bash
alembic history
```

> **Note**: Current migrations:
> - `90ea32905fbb` - Initial schema (items table)
> - `e3c1f4b2a9d0` - Security module (users, roles, permissions tables)

## Running the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Security & Authentication

### Overview

The application implements JWT-based authentication with role-based access control (RBAC):

- **Password Hashing**: Argon2 (industry-standard, secure against GPU attacks)
- **Token Format**: JWT (JSON Web Tokens)
- **Token Algorithm**: HS256
- **Roles**: `admin` (full access), `user` (read-only)
- **Permissions**: 12 predefined permissions across 6 modules

### Database Models

#### Person
Personal information for users:
```python
- id: int (primary key)
- first_name: str
- last_name: str
- email: str (unique)
- phone: str (optional)
- created_at: datetime
- updated_at: datetime
```

#### User
Authentication and authorization:
```python
- id: int (primary key)
- person_id: int (foreign key → Person)
- username: str (unique)
- password_hash: str (Argon2)
- is_active: bool (default: True)
- is_superuser: bool (default: False)
- last_login: datetime (nullable)
- created_at: datetime
- updated_at: datetime
- roles: List[Role] (many-to-many)
```

#### Role
User roles:
```python
- id: int (primary key)
- name: str (unique) - "admin", "user"
- description: str (nullable)
- is_system: bool (default: True - cannot be deleted)
- permissions: List[Permission] (many-to-many)
```

#### Permission
Fine-grained permissions:
```python
- id: int (primary key)
- code: str (unique) - e.g., "users.read", "roles.create"
- name: str
- description: str (nullable)
- module: str - "users", "roles", "permissions", "auth", "audit", "security"
- action: str - "read", "create", "update", "assign_role"
```

### Predefined Roles & Permissions

#### Admin Role
Full system access to all 12 permissions:
- `users.read`, `users.create`, `users.update`, `users.assign_role`
- `roles.read`, `roles.create`, `roles.update`
- `permissions.read`
- `auth.read_me`, `auth.register`
- `audit.read`
- `security.seed`

#### User Role
Read-only access:
- `users.read`
- `roles.read`
- `permissions.read`
- `auth.read_me`
- `audit.read`

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/token` | Login and get JWT token | No |
| GET | `/auth/me` | Get current user profile | Bearer Token |
| POST | `/auth/users/{user_id}/promote-to-admin` | Promote user to admin | users.update |
| GET | `/auth/roles` | List all roles | roles.read |
| GET | `/auth/permissions` | List all permissions | permissions.read |
| POST | `/auth/users/{user_id}/roles` | Assign role to user | users.assign_role |

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/items/` | List all items (paginated) |
| GET | `/items/{id}` | Get item by ID |
| POST | `/items/` | Create new item |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with welcome message |
| GET | `/health` | Health check endpoint |

## Scripts

### Seed Security (Roles & Permissions)

The `seed_security.py` script manages the database initialization for security features.

#### Seed only roles and permissions
```bash
python -m app.scripts.seed_security
```

Output:
```
✓ Security catalog seeded: 2 roles (admin, user) and 12 permissions
✓ Security seed completed successfully
```

#### Promote existing user to superuser
```bash
python -m app.scripts.seed_security --admin-username john --make-superuser
```

#### Create superuser directly
```bash
python -m app.scripts.seed_security \
  --admin-username admin \
  --admin-password MySecurePass123! \
  --admin-email admin@example.com \
  --make-superuser
```

Output:
```
✓ Security catalog seeded: 2 roles (admin, user) and 12 permissions
✓ Superuser 'admin' created with admin role
✓ Security seed completed successfully
```

#### View help
```bash
python -m app.scripts.seed_security --help
```

## Usage Examples

### 1. Register a New User

**Request:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!",
    "person": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true,
  "is_superuser": false,
  "person": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "roles": [
    {
      "id": 2,
      "name": "user",
      "description": "Regular user with read-only access",
      "permissions": [...]
    }
  ],
  "created_at": "2026-03-26T10:30:00",
  "updated_at": "2026-03-26T10:30:00"
}
```

### 2. Login and Get Token

**Request:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=SecurePassword123!"
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Access Protected Endpoint

Include the token in the Authorization header:

**Request:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true,
  "is_superuser": false,
  "person": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "roles": [...],
  "created_at": "2026-03-26T10:30:00",
  "updated_at": "2026-03-26T10:30:00"
}
```

### 4. Authorize in Swagger UI

1. Open http://localhost:8000/docs
2. Click the "Authorize" button (top right)
3. Enter your token in the "Value" field: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
4. Click "Authorize"

Now you can test protected endpoints directly from Swagger with your token.

### 5. Promote User to Admin (Admin Only)

**Request:**
```bash
curl -X POST http://localhost:8000/auth/users/1/promote-to-admin \
  -H "Authorization: Bearer <admin-token>"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true,
  "is_superuser": false,
  "person": {...},
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "Full system access",
      "permissions": [...]
    }
  ],
  "created_at": "2026-03-26T10:30:00",
  "updated_at": "2026-03-26T10:30:00"
}
```

### 6. List All Roles (Requires roles.read permission)

**Request:**
```bash
curl -X GET http://localhost:8000/auth/roles \
  -H "Authorization: Bearer <token>"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "admin",
    "description": "Full system access",
    "permissions": [
      {
        "id": 1,
        "code": "users.read",
        "name": "View users",
        "module": "users",
        "action": "read"
      },
      ...
    ]
  },
  {
    "id": 2,
    "name": "user",
    "description": "Regular user with read-only access",
    "permissions": [...]
  }
]
```

## Complete Workflow Example

### Step 1: Initialize the database
```bash
# Run migrations
alembic upgrade head

# Seed security catalog (roles & permissions)
python -m app.scripts.seed_security

# Or create a superuser directly
python -m app.scripts.seed_security \
  --admin-username superadmin \
  --admin-password MySecurePass! \
  --admin-email superadmin@example.com \
  --make-superuser
```

### Step 2: Start the application
```bash
uvicorn app.main:app --reload
```

### Step 3: Register a regular user
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "Pass123!",
    "person": {
      "first_name": "User",
      "last_name": "One",
      "email": "user1@example.com"
    }
  }'
# Returns user ID in response
```

### Step 4: Login with the regular user
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=Pass123!"
# Returns access token
```

### Step 5: Test protected endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <user-token>"
```

### Step 6: Superadmin promotes user to admin
```bash
# Get the superadmin token first
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=superadmin&password=MySecurePass!"

# Use the superadmin token to promote user1 (ID 2)
curl -X POST http://localhost:8000/auth/users/2/promote-to-admin \
  -H "Authorization: Bearer <superadmin-token>"
```

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

## Troubleshooting

### JWT Token Issues
- **Invalid or expired token**: Obtain a new token via `/auth/token`
- **Secret key mismatch**: Ensure `SECRET_KEY` in `.env` matches across all instances
- **Token format**: Always include `Bearer ` prefix: `Authorization: Bearer <token>`

### Database Connection
- **PostgreSQL not found**: Verify database URL in `.env` and that PostgreSQL is running
- **MySQL not found**: Verify database URL and that MySQL service is running
- **Migration errors**: Run `alembic downgrade -1` and check for conflicts

### Permission Denied
- **401 Unauthorized**: User not authenticated or token expired
- **403 Forbidden**: User lacks required permission. Check role assignments via `/auth/roles`

## License

[MIT License](LICENSE)