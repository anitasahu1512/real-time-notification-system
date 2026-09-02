from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.notification import router
from app.routes.auth import router as auth_router

from app.websocket.main import router as websocket_router
from app.services.pubsub import subscribe_notifications
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber_task = asyncio.create_task(
        subscribe_notifications()
    )

    try:
        yield
    finally:
        subscriber_task.cancel()

        try:
            await subscriber_task
        except asyncio.CancelledError:
            print("Redis subscriber task cancelled.")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(websocket_router)
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
