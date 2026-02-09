from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from .psi import psi
from .schema import QualityMetric, QualityReport


@dataclass(frozen=True)
class QualityConfig:
    drift_quantile: float = 0.8
    psi_bins: int = 12


def build_quality_report(df: pd.DataFrame, dataset: str, cfg: QualityConfig = QualityConfig()) -> QualityReport:
    num_cols = [c for c in df.columns if c not in {"user_id", "event_date"}]

    metrics: list[QualityMetric] = []

    # missingness
    miss = df[num_cols].isna().mean().sort_values(ascending=False)
    metrics.append(
        QualityMetric(
            name="missingness_max",
            value=float(miss.max()) if len(miss) else 0.0,
            meta={"top": miss.head(10).to_dict()},
        )
    )

    # ranges (sanity)
    desc = df[num_cols].describe().T[["min", "max", "mean", "std"]].to_dict(orient="index")
    metrics.append(QualityMetric(name="numeric_summary", value=1.0, meta=desc))

    # drift
    if "event_date" in df.columns:
        cut = df["event_date"].quantile(cfg.drift_quantile)
        ref = df[df["event_date"] <= cut]
        recent = df[df["event_date"] > cut]

        scores = {c: psi(ref[c].values, recent[c].values, bins=cfg.psi_bins) for c in num_cols}
        top = dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:15])
        metrics.append(QualityMetric(name="drift_psi_top", value=float(max(scores.values()) if scores else 0.0), meta=top))

    metrics.append(QualityMetric(name="generated_at", value=1.0, meta={"ts": datetime.utcnow().isoformat()}))

    return QualityReport(dataset=dataset, rows=int(df.shape[0]), columns=int(df.shape[1]), metrics=metrics)
