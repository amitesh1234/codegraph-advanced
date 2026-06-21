# Deployment

## Local (development)

Prerequisites: Docker, Python 3.12+, git.

1. Start Neo4j:
```bash
   docker compose up -d neo4j
```
   Neo4j Browser: http://localhost:7474 (user `neo4j`, password `password`)

2. Run the API:
```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
```
   API docs: http://localhost:8000/docs

3. Onboard a repo (local path or public git URL):
```bash
   curl -X POST http://localhost:8000/onboard \
     -H "Content-Type: application/json" \
     -d '{"repo_path": "https://github.com/psf/requests"}'
```

## Full stack in Docker

Bring up Neo4j + the API together:
```bash
docker compose up --build
```
The API reaches Neo4j at `bolt://neo4j:7687` (the compose service name).

Environment variables (set in `docker-compose.yml` or `.env`):

| Variable         | Default                | Purpose                    |
|------------------|------------------------|----------------------------|
| `NEO4J_URI`      | `bolt://localhost:7687`| Neo4j connection (use `bolt://neo4j:7687` in Docker) |
| `NEO4J_USER`     | `neo4j`                | Neo4j username             |
| `NEO4J_PASSWORD` | `password`             | Neo4j password (change it) |
| `MEMORY_DB`      | `memory.db`            | SQLite analysis-history file |

> If using the git-URL feature, ensure `git` is installed in the API image
> (`RUN apt-get update && apt-get install -y git` in the Dockerfile).

## Cloud (managed Neo4j)

For a hosted demo, point the API at **Neo4j AuraDB Free** instead of the Docker Neo4j:
- Set `NEO4J_URI` to your Aura `neo4j+s://...` connection string, plus its user/password.
- Deploy the API container to Railway / Render / Fly.io.
- Note: AuraDB Free has size limits and auto-pauses when idle (just resume it).