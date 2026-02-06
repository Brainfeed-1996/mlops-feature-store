from fastapi import APIRouter, HTTPException

from feature_store_api.feature_store.materialize import materialize_feature_view
from feature_store_api.feature_store.online import OnlineStore
from feature_store_api.feature_store.registry import Registry

router = APIRouter(tags=["features"])


@router.post("/materialize/{feature_view}")
async def materialize(feature_view: str) -> dict:
    fv = Registry.instance().get_feature_view(feature_view)
    if not fv:
        raise HTTPException(status_code=404, detail="unknown feature_view")
    n = await materialize_feature_view(fv)
    return {"materialized": fv.name, "rows": n}


@router.get("/online/{feature_view}/{entity_id}")
async def get_online(feature_view: str, entity_id: str) -> dict:
    fv = Registry.instance().get_feature_view(feature_view)
    if not fv:
        raise HTTPException(status_code=404, detail="unknown feature_view")

    online = OnlineStore.instance()
    data = await online.get_entity_features(fv, entity_id)
    if data is None:
        raise HTTPException(status_code=404, detail="no features for entity")
    return {"feature_view": fv.name, "entity_id": entity_id, "features": data}
