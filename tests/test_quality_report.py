import pandas as pd

from feature_store_api.quality import build_quality_report


def test_quality_report_smoke():
    df = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2],
            "event_date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-01", "2026-01-02"]),
            "events_total": [1, 2, 0, 3],
            "c_login": [0, 1, 0, 1],
            "c_view": [1, 1, 0, 2],
            "c_support": [0, 0, 0, 0],
            "c_purchase": [0, 1, 0, 0],
            "purchase_amount": [0.0, 10.0, 0.0, 0.0],
            "purchase_amount_7d": [0.0, 10.0, 0.0, 0.0],
            "days_since_last_activity": [0, 0, 1, 0],
        }
    )
    rep = build_quality_report(df, dataset="x")
    assert rep.rows == 4
    assert any(m.name == "drift_psi_top" for m in rep.metrics)
