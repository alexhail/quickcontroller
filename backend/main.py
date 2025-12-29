from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.apps import router as apps_router
from api.v1.auth import router as auth_router
from apps.command_center import app as command_center_app
from apps.connection_manager import get_connection_manager
from apps.framework.registry import get_registry
from core.config import settings
from db.postgres import close_pool, init_pool
from db.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_pool()
    await init_redis()

    # Register apps
    registry = get_registry()
    registry.register(command_center_app)

    # Start connection manager
    connection_manager = get_connection_manager()
    await connection_manager.start()

    yield

    # Shutdown
    await connection_manager.stop()
    await close_pool()
    await close_redis()


app = FastAPI(
    title="Quick Controller",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(apps_router, prefix="/api/v1")

# Mount command center routes
app.include_router(
    command_center_app.routes,
    prefix=f"/api/v1/apps/{command_center_app.app_id}",
    tags=[command_center_app.display_name],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
