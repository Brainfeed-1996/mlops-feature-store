from fastapi import FastAPI

from feature_store_api.api.routes import features, offline, registry

app = FastAPI(title="mlops-feature-store", version="0.1.0")

app.include_router(features.router)
app.include_router(offline.router)
app.include_router(registry.router)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}
