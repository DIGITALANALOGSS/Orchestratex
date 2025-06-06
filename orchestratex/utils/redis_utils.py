import redis
from typing import Any, List, Dict
from orchestratex.config import get_settings

settings = get_settings()

class RedisManager:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def publish_message(self, channel: str, message: Any) -> None:
        """Publish a message to a channel"""
        self.client.publish(channel, message)

    def subscribe(self, channel: str):
        """Subscribe to a channel"""
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        return pubsub

    def get_messages(self, channel: str) -> List[Dict]:
        """Get all messages from a channel"""
        pubsub = self.subscribe(channel)
        messages = []
        for message in pubsub.listen():
            if message['type'] == 'message':
                messages.append(message)
        pubsub.unsubscribe()
        return messages

    def set_data(self, key: str, value: Any, expire: int = None) -> None:
        """Set data with optional expiration"""
        self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)

    def get_data(self, key: str) -> Any:
        """Get data by key"""
        return self.client.get(key)

    def delete_data(self, key: str) -> None:
        """Delete data by key"""
        self.client.delete(key)

    def set_hash(self, key: str, field: str, value: Any) -> None:
        """Set a field in a hash"""
        self.client.hset(key, field, value)

    def get_hash(self, key: str, field: str = None) -> Any:
        """Get a field from a hash or all fields if no field specified"""
        if field:
            return self.client.hget(key, field)
        return self.client.hgetall(key)
