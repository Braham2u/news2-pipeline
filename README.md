# NEWS2 Early-Warning Score API

A small healthcare service that computes the **National Early Warning
Score 2** (Royal College of Physicians, 2017) from patient vital signs.
It is the placeholder project for a research paper on designing and
integrating a CI/CD pipeline and Agile development into a healthcare
application.

## API

| Method | Path      | Description                              |
|--------|-----------|------------------------------------------|
| GET    | `/health` | Liveness probe (used by the CD pipeline) |
| POST   | `/score`  | Compute the NEWS2 score for observations |

## Run locally

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
# open http://localhost:8000/docs
```

## Quality gate (run what CI runs)

```bash
ruff check .
pytest -q
```

## Container

```bash
docker build -t news2 .
docker run -p 8000:8000 news2
curl http://localhost:8000/health
```

## Pipeline

- **CI** (`.github/workflows/ci.yml`): lint (ruff) + tests (pytest) on
  every push and pull request to `main`.
- **CD** (`.github/workflows/cd.yml`): on a successful CI run on `main`,
  builds the Docker image, publishes it to GitHub Container Registry
  (GHCR), and smoke-tests the published image's `/health` endpoint.
