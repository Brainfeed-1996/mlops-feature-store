"""
Streaming integration for feature store (Kafka/Redis Streams).
"""

import json
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


@dataclass
class StreamMessage:
    """Message from streaming source."""
    key: str
    value: Dict
    timestamp: datetime
    topic: str
    partition: int
    offset: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "topic": self.topic,
            "partition": self.partition,
            "offset": self.offset
        }


class StreamConsumer(ABC):
    """Abstract base class for stream consumers."""
    
    @abstractmethod
    async def start(self):
        """Start consuming messages."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop consuming."""
        pass
    
    @abstractmethod
    async def consume(self, timeout_ms: int = 1000) -> Optional[StreamMessage]:
        """Consume a single message."""
        pass


class KafkaConsumerAdapter(StreamConsumer):
    """Kafka consumer adapter for feature ingestion."""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "feature-events",
        group_id: str = "feature-store-consumer",
        auto_offset_reset: str = "latest"
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: Where to start consuming
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self._consumer = None
        self._running = False
    
    async def start(self):
        """Start the consumer."""
        try:
            from aiokafka import AIOKafkaConsumer
            
            self._consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda m: json.loads(m.decode())
            )
            
            await self._consumer.start()
            self._running = True
            logger.info(f"Started Kafka consumer for topic {self.topic}")
        except ImportError:
            logger.warning("aiokafka not installed, using mock consumer")
            self._consumer = MockKafkaConsumer(self.topic)
            await self._consumer.start()
    
    async def stop(self):
        """Stop the consumer."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            logger.info("Stopped Kafka consumer")
    
    async def consume(self, timeout_ms: int = 1000) -> Optional[StreamMessage]:
        """Consume a message."""
        if not self._consumer:
            return None
        
        try:
            # Use asyncio.wait_for to implement timeout
            messages = await asyncio.wait_for(
                self._consumer.getmany(timeout_ms=timeout_ms),
                timeout=timeout_ms / 1000.0
            )
            
            for topic_partition, msgs in messages.items():
                for msg in msgs:
                    return StreamMessage(
                        key=msg.key.decode() if msg.key else "",
                        value=msg.value,
                        timestamp=msg.timestamp,
                        topic=msg.topic,
                        partition=msg.partition,
                        offset=msg.offset
                    )
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error consuming message: {e}")
        
        return None


class MockKafkaConsumer:
    """Mock Kafka consumer for testing."""
    
    def __init__(self, topic: str):
        self.topic = topic
        self._messages = []
        self._running = False
    
    async def start(self):
        self._running = True
        logger.info("Started mock Kafka consumer")
    
    async def stop(self):
        self._running = False
        logger.info("Stopped mock Kafka consumer")
    
    async def getmany(self, timeout_ms: int = 1000):
        """Get messages (mock)."""
        await asyncio.sleep(timeout_ms / 1000.0)
        if self._messages:
            topic_partition = f"{self.topic}-0"
            msgs = [self._messages.pop(0)]
            return {topic_partition: msgs}
        return {}
    
    def add_message(self, message: StreamMessage):
        """Add a message for testing."""
        self._messages.append(message)


class RedisStreamConsumer(StreamConsumer):
    """Redis Streams consumer."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        stream_name: str = "feature-events",
        group_name: str = "feature-store-group"
    ):
        """
        Initialize Redis Streams consumer.
        
        Args:
            host: Redis host
            port: Redis port
            stream_name: Stream name
            group_name: Consumer group name
        """
        self.host = host
        self.port = port
        self.stream_name = stream_name
        self.group_name = group_name
        self._client = None
        self._running = False
    
    async def start(self):
        """Start the consumer."""
        try:
            import aioredis
            
            self._client = aioredis.from_url(
                f"redis://{self.host}:{self.port}",
                decode_responses=True
            )
            
            # Create consumer group if not exists
            try:
                await self._client.xgroup_create(
                    self.stream_name,
                    self.group_name,
                    mkstream=True
                )
            except Exception:
                pass  # Group already exists
            
            self._running = True
            logger.info(f"Started Redis Stream consumer for {self.stream_name}")
        except ImportError:
            logger.warning("aioredis not installed, using mock consumer")
            self._client = MockRedisStreamConsumer(self.stream_name)
            await self._client.start()
    
    async def stop(self):
        """Stop the consumer."""
        self._running = False
        if self._client:
            await self._client.close()
            logger.info("Stopped Redis Stream consumer")
    
    async def consume(self, timeout_ms: int = 1000) -> Optional[StreamMessage]:
        """Consume a message."""
        if not self._client:
            return None
        
        try:
            # Read from stream
            messages = await self._client.xreadgroup(
                self.group_name,
                "consumer1",
                {self.stream_name: ">"},
                count=1,
                block=timeout_ms
            )
            
            if messages:
                stream_name, stream_messages = messages[0]
                for msg_id, data in stream_messages:
                    return StreamMessage(
                        key=data.get("entity_id", ""),
                        value=data,
                        timestamp=datetime.utcnow(),
                        topic=stream_name,
                        partition=0,
                        offset=int(msg_id.split("-")[0])
                    )
        except Exception as e:
            logger.error(f"Error consuming Redis message: {e}")
        
        return None


class MockRedisStreamConsumer:
    """Mock Redis Streams consumer for testing."""
    
    def __init__(self, stream_name: str):
        self.stream_name = stream_name
        self._messages = []
    
    async def start(self):
        logger.info("Started mock Redis Stream consumer")
    
    async def close(self):
        logger.info("Stopped mock Redis Stream consumer")
    
    def add_message(self, message: StreamMessage):
        self._messages.append(message)


class FeatureStreamProcessor:
    """Process feature data from streams."""
    
    def __init__(
        self,
        consumer: StreamConsumer,
        feature_store=None,
        batch_size: int = 100
    ):
        """
        Initialize processor.
        
        Args:
            consumer: Stream consumer instance
            feature_store: Feature store instance
            batch_size: Batch size for ingestion
        """
        self.consumer = consumer
        self.feature_store = feature_store
        self.batch_size = batch_size
        self._running = False
        self._batch: List[StreamMessage] = []
    
    async def start(self, handler: Callable = None):
        """
        Start processing stream.
        
        Args:
            handler: Custom message handler
        """
        await self.consumer.start()
        self._running = True
        
        logger.info("Starting stream processor...")
        
        while self._running:
            msg = await self.consumer.consume()
            
            if msg:
                self._batch.append(msg)
                
                # Process batch when full
                if len(self._batch) >= self.batch_size:
                    await self._process_batch(handler)
        
        # Process remaining batch
        if self._batch:
            await self._process_batch(handler)
    
    async def stop(self):
        """Stop processing."""
        self._running = False
        await self.consumer.stop()
    
    async def _process_batch(self, handler: Callable = None):
        """Process a batch of messages."""
        batch = self._batch
        self._batch = []
        
        logger.info(f"Processing batch of {len(batch)} messages")
        
        try:
            if handler:
                await handler(batch)
            elif self.feature_store:
                # Default: ingest to feature store
                for msg in batch:
                    await self._ingest_message(msg)
            
            logger.info(f"Successfully processed {len(batch)} messages")
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            # Re-add messages to batch for retry
            self._batch.extend(batch)
    
    async def _ingest_message(self, msg: StreamMessage):
        """Ingest a single message."""
        if self.feature_store:
            await self.feature_store.ingest(
                feature_view=msg.value.get("feature_view", "default"),
                rows=[msg.value]
            )


async def run_stream_consumer(
    topic: str = "feature-events",
    bootstrap_servers: str = "localhost:9092"
):
    """Run a simple stream consumer."""
    from feature_store_api import FeatureStore
    
    # Create consumer
    consumer = KafkaConsumerAdapter(
        bootstrap_servers=bootstrap_servers,
        topic=topic
    )
    
    # Create processor
    processor = FeatureStreamProcessor(
        consumer=consumer,
        batch_size=50
    )
    
    # Start processing
    await processor.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Feature Store Stream Consumer")
    parser.add_argument("--topic", default="feature-events")
    parser.add_argument("--servers", default="localhost:9092")
    args = parser.parse_args()
    
    asyncio.run(run_stream_consumer(args.topic, args.servers))
