# mlops-feature-store

A **Feast-like** (but deliberately simplified) feature store built with:

- **FastAPI** (serving + admin API)
- **PostgreSQL** (offline store)
- **Redis** (online store)
- **YAML registry** (feature definitions)

This repo is designed as a high-complexity reference project: clean layering, async IO, Docker Compose, and a small demo pipeline.

**Author: Olivier Robert-Duboille**

## Notebooks (added)

These notebooks add an **offline Parquet/CSV-based** pipeline (useful even if you run the full Postgres/Redis stack):
- `notebooks/01_offline_feature_generation.ipynb` — generate raw events + compute daily features (DuckDB)
- `notebooks/02_training_with_features.ipynb` — train a baseline model consuming materialized features
- `notebooks/03_data_quality_and_leakage_checks.ipynb` — quality + drift checks (executed outputs saved)

## CLI (quality)
Generate a quality report from a feature table:
```bash
pip install -e .[quality]
mfs quality --input registry/offline/features_daily.csv --out out/quality_report.json
```

## What you get

- Registry-driven `FeatureView` definitions (entities, features, TTL, source table)
- Offline store: **Postgres or SQLite**
- Online store: **Redis** (or in-memory fallback)
- Offline retrieval helper: "latest row per entity" (simplified)
- Materialization job: offline → online
- FastAPI endpoints:
  - `GET /healthz`
  - `POST /registry/reload`
  - `POST /offline/ingest/{feature_view}`
  - `POST /materialize/{feature_view}`
  - `GET /online/{feature_view}/{entity_id}`

## Quickstart (Docker)

```bash
docker compose up --build
```

Seed demo data:

```bash
python -m venv .venv && . .venv/Scripts/activate
pip install -e .
python scripts/demo_ingest.py
```

Query online store:

```bash
curl http://localhost:8000/online/user_features/123
```

## Quickstart (no Docker: SQLite + in-memory online store)

```bash
python -m venv .venv && . .venv/Scripts/activate
pip install -e .
set FEATURE_STORE_DATABASE_URL=sqlite+aiosqlite:///./feature_store.db
set FEATURE_STORE_ONLINE_BACKEND=memory
uvicorn feature_store_api.main:app --reload
```

Create a minimal SQLite table (one-time):

```sql
CREATE TABLE user_features (
  user_id INTEGER NOT NULL,
  event_ts TEXT NOT NULL,
  country TEXT,
  age INTEGER,
  purchases_7d REAL,
  PRIMARY KEY (user_id, event_ts)
);
```

Ingest + materialize + fetch:

```bash
curl -X POST http://localhost:8000/offline/ingest/user_features \
  -H "content-type: application/json" \
  -d '{"rows": [{"user_id": 123, "event_ts": "2026-02-01T00:00:00+00:00", "country": "FR", "age": 29, "purchases_7d": 3.0}]}'

curl -X POST http://localhost:8000/materialize/user_features
curl http://localhost:8000/online/user_features/123
```

## Design notes

This is **not** a production feature store.
It is a learning-oriented implementation inspired by Feast concepts:

- registry (defs)
- offline store
- online store
- materialization

See `registry/feature_views.yaml`.

## License

MIT
