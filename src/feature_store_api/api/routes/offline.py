from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from feature_store_api.feature_store.ingest import ingest_rows
from feature_store_api.feature_store.registry import Registry

router = APIRouter(tags=["offline"])


class IngestRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(..., description="List of rows to insert in offline table")


@router.post("/offline/ingest/{feature_view}")
async def ingest(feature_view: str, req: IngestRequest) -> dict:
    fv = Registry.instance().get_feature_view(feature_view)
    if not fv:
        raise HTTPException(status_code=404, detail="unknown feature_view")

    n = await ingest_rows(fv, req.rows)
    return {"ingested": fv.name, "rows": n}
