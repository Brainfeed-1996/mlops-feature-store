from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from .models import FeatureView

class RetrievalStrategy(ABC):
    @abstractmethod
    async def retrieve(self, fv: FeatureView, entity_id: str, store: Any) -> Optional[Dict[str, Any]]:
        pass

class DirectRetrievalStrategy(RetrievalStrategy):
    async def retrieve(self, fv: FeatureView, entity_id: str, store: Any) -> Optional[Dict[str, Any]]:
        return await store._direct_get(fv, entity_id)

class FallbackRetrievalStrategy(RetrievalStrategy):
    def __init__(self, primary: RetrievalStrategy, fallback_data: Dict[str, Any]):
        self.primary = primary
        self.fallback_data = fallback_data

    async def retrieve(self, fv: FeatureView, entity_id: str, store: Any) -> Optional[Dict[str, Any]]:
        result = await self.primary.retrieve(fv, entity_id, store)
        return result if result else self.fallback_data
