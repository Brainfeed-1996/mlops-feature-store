# Architecture

## Overview

The MLOps Feature Store is a Feast-like system for managing ML features in production. It provides:
- Offline storage for training data
- Online storage for real-time inference
- Point-in-time joins to prevent data leakage
- Data quality and drift monitoring

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Feature Store                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │   Client    │    │   CLI/API   │    │   Registry          │ │
│  │  (Python)   │───▶│  (FastAPI)  │───▶│  (YAML/JSON)       │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Orchestrator                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │Materializer│  │  Monitor   │  │ Quality Checker │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         ▼                  ▼                  ▼                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  Offline    │    │   Online    │    │   Streaming         │ │
│  │  Store      │    │  Store      │    │   (Kafka)          │ │
│  │ (PostgreSQL)│    │  (Redis)    │    │                     │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### API Layer (FastAPI)

- RESTful endpoints for all operations
- Async support for high concurrency
- OpenAPI documentation at `/docs`
- Health checks and metrics

### Registry

- YAML-based feature definitions
- Version control for features
- Entity and feature schemas
- TTL and source configuration

### Offline Store (PostgreSQL)

- Historical feature storage
- Time-travel queries
- Point-in-time joins
- Batch materialization

### Online Store (Redis)

- Low-latency feature retrieval
- In-memory caching
- TTL-based expiration
- Batch lookups

### Streaming (Kafka)

- Real-time feature ingestion
- Stream processing
- Low-latency updates

### Monitoring

- Prometheus metrics
- Drift detection
- Data quality checks

## Data Flow

### Training Data Retrieval

```python
# Point-in-time join
features = store.get_historical_features(
    entity_df=entity_df,
    feature_views=["user_features"],
    timestamp_col="event_timestamp"
)
```

### Online Inference

```python
# Get single feature
feature = store.get_online("user_features", entity_id=123)

# Batch retrieval
features = store.get_online_batch("user_features", [123, 456])
```

### Materialization

```python
# Sync offline → online
store.materialize("user_features")
```

## Scalability

### Horizontal Scaling

- API servers: Stateless, scale behind load balancer
- Offline store: PostgreSQL read replicas
- Online store: Redis cluster

### Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Online lookup | < 1ms | 100K QPS |
| Batch lookup | < 10ms | 10K QPS |
| Materialization | Varies | 1M rows/min |

## Security

- API authentication (JWT)
- Role-based access control
- Audit logging
- Encrypted storage
