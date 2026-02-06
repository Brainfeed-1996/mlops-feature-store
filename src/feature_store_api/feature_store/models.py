from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    name: str
    value_type: str


@dataclass(frozen=True)
class Feature:
    name: str
    value_type: str


@dataclass(frozen=True)
class OfflineSource:
    table: str
    timestamp_column: str
    entity_column: str


@dataclass(frozen=True)
class FeatureView:
    name: str
    entity: Entity
    features: list[Feature]
    offline: OfflineSource
    ttl_seconds: int
