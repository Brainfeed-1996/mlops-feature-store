from fastapi import APIRouter

from feature_store_api.feature_store.registry import Registry

router = APIRouter(prefix="/registry", tags=["registry"])


@router.post("/reload")
async def reload_registry() -> dict:
    Registry.instance().reload()
    return {"reloaded": True, "feature_views": [fv.name for fv in Registry.instance().feature_views]}
