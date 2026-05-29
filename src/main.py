from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from contextlib import asynccontextmanager

from src.redis.service import redis_service
from src.router import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_service.connect()
    print("Connected to Redis")

    yield

    await redis_service.disconnect()
    print("Disconnected from Redis")


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])
