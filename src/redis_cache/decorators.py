import hashlib
import json
from src.redis_cache.service import redis_service
from functools import wraps
from typing import Any, Callable, Type, Optional

from pydantic import BaseModel


def cache(
    expire: int = 300,
    prefix: str = "",
    model: Optional[Type[BaseModel]] = None,
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # --- Генерация ключа ---
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

            # --- Попытка получить из кеша ---
            cached = await redis_service.get(cache_key)
            if cached is not None:

                # 👇 если указана модель — возвращаем Pydantic
                if model:
                    return model.model_validate_json(cached)

                return json.loads(cached)

            # --- Выполняем функцию ---
            result = await func(*args, **kwargs)

            if result is not None:
                # 👇 если это Pydantic модель
                if isinstance(result, BaseModel):
                    await redis_service.set(
                        cache_key,
                        result.model_dump_json(),
                        expire,
                    )
                else:
                    await redis_service.set(
                        cache_key,
                        json.dumps(result),
                        expire,
                    )

            print("cache true\n\n\n\n")
            return result

        return wrapper

    return decorator
