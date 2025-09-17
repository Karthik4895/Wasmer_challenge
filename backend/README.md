# Backend Challenge: GraphQL API with Django + PostgreSQL

This project provides a GraphQL-based backend where users can create and manage deployed apps. Each user has a plan (`Hobby` or `Pro`), and each app is linked to a single owner.


## Tech Stack

- **Python 3.11+**
- **Django 4+** (async ORM support)
- **PostgreSQL** (via Docker)
- **GraphQL** via Graphene-Django (Relay-compatible)
- **Async DataLoader** for batching queries
- **Docker Compose** for DB setup



### 1. Clone and Setup Environment

```bash
git clone https://github.com/Karthik4895/Wasmer_challenge
cd Wasmer-challenge
python3.11 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

---

### 2. Start PostgreSQL via Docker

```bash
docker-compose up -d
```

---

### 3. Configure `.env`

Create a `.env` file in the root:

```
DB_NAME=django
DB_USER=django
DB_PASSWORD=django
DB_HOST=localhost
DB_PORT=5433 ( I had the issue with Port 5432 , thats why i have changed it to 5433)
```

---

### 4. Run Migrations and Load Data

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata users apps
```

---

### 5. Start the Server

```bash
python manage.py runserver
```

Access GraphiQL at:  http://localhost:8000/graphql/



### Query a User

```graphql
query {
  node(id: "u_1") {
    ... on UserType {
      id
      username
      plan
    }
  }
}
```

### Query an App

```graphql
query {
  node(id: "app_1") {
    ... on AppType {
      id
      active
    }
  }
}
```

### Upgrade User Plan

```graphql
mutation {
  upgradeAccount(userId: "u_1") {
    user {
      id
      plan
    }
  }
}
```


##  Fixture Files

Located in: `apps/core/fixtures/`

- `users.json` – Sample users (Hobby and Pro)
- `apps.json` – Sample deployed apps linked to users

---

## Cleanup

To stop Docker DB:

```bash
docker-compose down -v
```
