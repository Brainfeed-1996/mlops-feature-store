from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from feature_store_api.quality import QualityConfig, build_quality_report


def cmd_quality(args) -> int:
    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"missing input: {p}")

    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p)
    else:
        # parquet requires pyarrow/fastparquet
        df = pd.read_parquet(p)

    if "event_date" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_date"])

    rep = build_quality_report(df, dataset=args.dataset, cfg=QualityConfig())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rep.model_dump_json(indent=2), encoding="utf-8")
    print(rep.model_dump_json(indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mfs")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("quality", help="Generate a quality/drift report for a feature table")
    q.add_argument("--input", required=True, help="CSV or Parquet file")
    q.add_argument("--dataset", default="features")
    q.add_argument("--out", default="out/quality_report.json")
    q.set_defaults(fn=cmd_quality)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
