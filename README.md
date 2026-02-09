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
- Offline retrieval from Postgres (point-in-time-ish helper query patterns)
- Online retrieval from Redis (per-entity keying)
- Materialization job: offline → online
- FastAPI endpoints:
  - `GET /healthz`
  - `POST /registry/reload`
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
