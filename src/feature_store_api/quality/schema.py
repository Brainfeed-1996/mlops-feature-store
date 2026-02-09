from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class FeatureRow(BaseModel):
    user_id: int
    event_date: date
    events_total: int = Field(ge=0)
    c_login: int = Field(ge=0)
    c_view: int = Field(ge=0)
    c_support: int = Field(ge=0)
    c_purchase: int = Field(ge=0)
    purchase_amount: float = Field(ge=0)
    purchase_amount_7d: float = Field(ge=0)
    days_since_last_activity: int = Field(ge=0)


class QualityMetric(BaseModel):
    name: str
    value: float
    meta: dict[str, Any] = {}


class QualityReport(BaseModel):
    dataset: str
    rows: int
    columns: int
    metrics: list[QualityMetric]
