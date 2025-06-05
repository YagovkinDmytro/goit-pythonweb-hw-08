# FastAPI and REST API construction. Application architecture.

# Create docker container

```bash
docker run --name db-contacts -p 5432:5432 -e POSTGRES_USER="POSTGRES_USER" -e POSTGRES_PASSWORD="POSTGRES_PASSWORD" -e POSTGRES_DB="POSTGRES_DB" -d postgres
```

# Alembic migrations

Before this, you need to make all the necessary settings for migrations.

```bash
alembic init migrations
alembic revision --autogenerate -m 'Init'
alembic upgrade head
```

# Starting development server

```bash
fastapi dev main.py
- starts the development server.
```

Server started at http://127.0.0.1:8000

Documentation at http://127.0.0.1:8000/docs

Documentation at http://127.0.0.1:8000/redoc

```bash
fastapi run main.py
- starts the production server.
```

# Architecture of the project

```bash
├── migrations
│   ├── versions
│   │   └──name_of_version.py
├── src
│   ├── api
│   │   ├── utils.py
│   │   └── contacts.py
│   ├── services
│   │   └── contacts.py
│   ├── repository
│   │   └── contacts.py
│   ├── database
│   │   ├── models.py
│   │   └── db.py
│   ├── conf
│   │   └── config.py
│   └── schemas.py
├── .env
├── .env.examlpe
├── .gitignore
├── alembic.ini
├── poetry.lock
├── pyproject.toml
├── README.md
└── main.py
```
