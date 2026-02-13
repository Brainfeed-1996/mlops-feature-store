# MLOps Feature Store (Advanced)

Feast-like feature store with advanced capabilities for production ML systems.

## Features

### Core Features
- **Feature Views**: Registry-driven definitions (entities, features, TTL, source)
- **Offline Store**: PostgreSQL or SQLite with async support
- **Online Store**: Redis with in-memory fallback
- **Materialization**: Offline to online synchronization
- **Auto-Registration**: Automatic feature discovery and registration

### Advanced Features
- **Streaming Support**: Apache Kafka integration
- **Point-in-Time Joins**: Historical feature retrieval
- **Feature Versioning**: Track feature changes over time
- **Data Quality Checks**: Built-in validation and monitoring
- **Drift Detection**: Statistical drift detection for features
- **Monitoring**: Prometheus metrics integration

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/registry/reload` | POST | Reload registry |
| `/offline/ingest/{feature_view}` | POST | Ingest feature data |
| `/offline/query` | POST | Point-in-time query |
| `/materialize/{feature_view}` | POST | Materialize to online |
| `/materialize/all` | POST | Materialize all views |
| `/online/{feature_view}/{entity_id}` | GET | Get online feature |
| `/online/batch` | POST | Batch online retrieval |
| `/drift/{feature_view}` | GET | Drift analysis |
| `/metrics` | GET | Prometheus metrics |

## Installation

```bash
# Basic installation
pip install -e .

# With quality tools
pip install -e ".[quality]"

# With all extras
pip install -e ".[dev,quality]"
```

## Docker Quickstart

```bash
docker compose up --build
```

## Usage

### CLI Commands

```bash
# Start API server
mfs serve

# Ingest data
mfs ingest --view user_features --data data.json

# Materialize features
mfs materialize --view user_features

# Materialize all
mfs materialize-all

# Check data quality
mfs quality --input features.csv --out report.json

# Run drift analysis
mfs drift --view user_features --reference data.csv

# Auto-register features from directory
mfs register --path registry/*.yaml
```

### Python API

```python
from feature_store_api import FeatureStore

# Initialize store
store = FeatureStore()

# Register feature view
store.register_view("user_features", "registry/user_features.yaml")

# Ingest features
store.ingest("user_features", [
    {"user_id": 123, "event_ts": "2026-02-01T00:00:00", "purchases": 5}
])

# Point-in-time join
features = store.get_historical_features(
    entity_df=entity_df,
    feature_views=["user_features"],
    timestamp_col="event_timestamp"
)

# Materialize to online store
store.materialize("user_features")

# Retrieve online features
online = store.get_online("user_features", entity_ids=[123, 456])

# Check drift
drift = store.analyze_drift("user_features", reference_data)
```

## Architecture

```
mlops-feature-store/
├── src/feature_store_api/
│   ├── main.py              # FastAPI application
│   ├── registry.py          # Feature registry
│   ├── offline/            # Offline store (PostgreSQL)
│   │   ├── store.py
│   │   ├── models.py
│   │   └── queries.py
│   ├── online/              # Online store (Redis)
│   │   ├── store.py
│   │   └── cache.py
│   ├── materialization/     # Materialization jobs
│   │   ├── jobs.py
│   │   └── scheduler.py
│   ├── streaming/          # Kafka integration
│   │   ├── consumer.py
│   │   └── producer.py
│   ├── monitoring/        # Metrics & drift
│   │   ├── metrics.py
│   │   └── drift.py
│   └── quality/           # Data quality
│       ├── checks.py
│       └── reports.py
├── tests/
├── registry/              # Feature definitions
├── notebooks/            # Examples
└── docker-compose.yml
```

## Feature Definitions

```yaml
feature_view: user_features
entities:
  - name: user_id
    dtype: int64
features:
  - name: country
    dtype: string
  - name: purchases_7d
    dtype: float64
  - name: age
    dtype: int32
source: user_events
ttl: 7d
join_keys:
  - user_id
description: User purchasing behavior features
version: 1
tags:
  owner: ml-team
  priority: high
```

## Streaming Integration

```python
from feature_store_api.streaming import KafkaConsumer

# Create consumer
consumer = KafkaConsumer(
    topic="user-events",
    bootstrap_servers="localhost:9092",
    feature_store=store
)

# Start consuming
consumer.start()
```

## Monitoring

### Prometheus Metrics

```bash
# Expose metrics
curl http://localhost:8000/metrics
```

Available metrics:
- `feature_store_ingestion_total`
- `feature_store_materialization_duration_seconds`
- `feature_store_online_latency_seconds`
- `feature_store_drift_score`

### Drift Detection

```python
# Calculate drift
drift_score = store.analyze_drift(
    "user_features",
    reference_data=reference_df,
    method="kl_divergence"
)

if drift_score > 0.5:
    alert("High drift detected!")
```

## Data Quality

```python
from feature_store_api.quality import run_quality_checks

# Run quality checks
results = run_quality_checks(
    data=df,
    rules=[
        {"column": "user_id", "check": "not_null"},
        {"column": "age", "check": "between(0, 150)"},
        {"column": "purchases", "check": ">= 0"}
    ]
)

print(results.summary)
```

## Notebooks

- `notebooks/01_offline_feature_generation.ipynb` - Feature engineering
- `notebooks/02_training_with_features.ipynb` - Model training
- `notebooks/03_data_quality_and_leakage_checks.ipynb` - Quality & drift

## License

MIT
