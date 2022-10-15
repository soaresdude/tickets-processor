from typing import List

from redis.client import Redis


class RedisClient:
    instance: Redis = Redis(host="redis", port=6379)

    def append_to_key(self, key: str, value: str):
        return self.instance.rpush(key, value)

    def retrieve_list(self, key: str) -> List:
        return [v.decode() for v in self.instance.lrange(key, 0, -1)]
