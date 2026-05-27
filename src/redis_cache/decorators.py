import hashlib
import json
from src.redis_cache.service import redis_service
from functools import wraps
from typing import Any, Callable, Type, Optional

from pydantic import BaseModel


def cache(
    expire: int,
    prefix: str,
    model: Optional[Type[BaseModel]] = None,
):

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            cache_parts = [prefix if prefix else func.__name__]

            for arg in args:
                if not hasattr(arg, "__await__") and not hasattr(arg, "execute"):
                    if hasattr(arg, "id"):
                        cache_parts.append(f"id:{arg.id}")
                    else:
                        cache_parts.append(str(arg))

            for key, value in kwargs.items():
                if key not in ["session"]:
                    if hasattr(value, "id"):
                        cache_parts.append(f"{key}:{value.id}")
                    else:
                        cache_parts.append(f"{key}:{value}")

            cache_key = hashlib.md5("_".join(cache_parts).encode()).hexdigest()

            cached = await redis_service.get(cache_key)
            if cached is not None:
                if isinstance(cached, list):
                    return [model.model_validate(json.loads(c)) for c in cached]
                else:
                    return model.model_validate(json.loads(cached))

            result = await func(*args, **kwargs)
            if result is not None:
                if isinstance(result, BaseModel):
                    await redis_service.set(
                        cache_key,
                        result.model_dump_json(),
                        expire,
                    )
                elif isinstance(result, list) and result:
                    result_to_json = [r.model_dump_json() for r in result]
                    await redis_service.set(cache_key, result_to_json, expire)
                else:
                    await redis_service.set(cache_key, result, expire)

            return result

        return wrapper

    return decorator
