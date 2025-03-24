from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from src.auth.db import User
from collections.abc import AsyncIterator
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.auth.auth_backend import auth_backend, fastapi_users, current_active_user
from src.auth.schemas import UserRead, UserCreate
from src.links.router import router as links_router
from src.tasks.router import router as celery_router
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://127.0.0.1")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# API endpoints
app.include_router(links_router)
app.include_router(celery_router)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@app.get("/unauthenticated-route")
async def unauthenticated_route():
    return {"message": "Hello human!"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, host="127.0.0.1", port=8000, log_level="info")