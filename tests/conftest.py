import os
import tempfile
from pathlib import Path

# IMPORTANT: set env vars at import time so they apply before importing the app.
_db_dir = Path(tempfile.mkdtemp(prefix="feature_store_test_"))
_db_path = _db_dir / "feature_store_test.db"

os.environ.setdefault("FEATURE_STORE_DATABASE_URL", f"sqlite+aiosqlite:///{_db_path.as_posix()}")
os.environ.setdefault("FEATURE_STORE_ONLINE_BACKEND", "memory")
os.environ.setdefault("FEATURE_STORE_REDIS_URL", "")

# Ensure registry path is correct when tests are run from repo root.
os.environ.setdefault("FEATURE_STORE_REGISTRY_PATH", str(Path("registry") / "feature_views.yaml"))
