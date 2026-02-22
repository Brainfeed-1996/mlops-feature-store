from __future__ import annotations

from pathlib import Path

import yaml

from feature_store_api.core.config import settings
from feature_store_api.feature_store.models import Entity, Feature, FeatureView, OfflineSource


class Registry:
    _instance: "Registry | None" = None

    def __init__(self, registry_path: str) -> None:
        self.registry_path = Path(registry_path)
        self.feature_views: list[FeatureView] = []
        self.reload()

    @classmethod
    def instance(cls) -> "Registry":
        if cls._instance is None:
            cls._instance = Registry(settings.registry_path)
        return cls._instance

    def reload(self) -> None:
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry file not found: {self.registry_path}")

        raw = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        fvs: list[FeatureView] = []
        for idx, fv in enumerate(raw.get("feature_views", [])):
            try:
                entity = Entity(**fv["entity"])
                offline = OfflineSource(**fv["offline"])
                features = [Feature(**f) for f in fv["features"]]
                fvs.append(
                    FeatureView(
                        name=fv["name"],
                        entity=entity,
                        features=features,
                        offline=offline,
                        ttl_seconds=int(fv.get("ttl_seconds", 0)),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid feature_view at index {idx}: {fv}") from exc
        self.feature_views = fvs

    def get_feature_view(self, name: str) -> FeatureView | None:
        for fv in self.feature_views:
            if fv.name == name:
                return fv
        return None
