from fastapi.testclient import TestClient


def test_registry_reload():
    from feature_store_api.main import app

    c = TestClient(app)
    r = c.post("/registry/reload")
    assert r.status_code == 200
    assert "user_features" in r.json()["feature_views"]
