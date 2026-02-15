# MLOps Feature Store (Advanced)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![GitHub Stars](https://img.shields.io/github/stars/mlops-feature-store?style=flat-square)

</div>

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

## Quick Start

### Installation

```bash
# Basic installation
pip install -e .

# With quality tools
pip install -e ".[quality]"

# With all extras
pip install -e ".[dev,quality]"
```

### Docker Quickstart

```bash
docker compose up --build
```

### CLI Usage

```bash
# Start API server
mfs serve

# Ingest data
mfs ingest --view user_features --data data.json

# Materialize features
mfs materialize --view user_features

# Check data quality
mfs quality --input features.csv --out report.json

# Run drift analysis
mfs drift --view user_features --reference data.csv
```

## API Endpoints

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

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [Feature Definitions](docs/FEATURES.md) - YAML schema reference
- [API Reference](docs/API.md) - REST API documentation

## Notebooks

- `notebooks/01_offline_feature_generation.ipynb` - Feature engineering
- `notebooks/02_training_with_features.ipynb` - Model training
- `notebooks/03_data_quality_and_leakage_checks.ipynb` - Quality & drift

## License

MIT
