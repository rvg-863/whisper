import uuid
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from server.config import settings
from server.database import async_session
from server.services.auth import decode_access_token
from server.routes.auth import router as auth_router
from server.routes.keys import router as keys_router
from server.routes.servers import router as servers_router
from server.routes.channels import router as channels_router
from server.ws.manager import manager
from server.ws.messaging import handle_ws_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(settings.redis_url)
    yield
    await app.state.redis.close()


app = FastAPI(title="Whisper", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(keys_router)
app.include_router(servers_router)
app.include_router(channels_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id_str = decode_access_token(token)
    if not user_id_str:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = uuid.UUID(user_id_str)
    await manager.connect(websocket, user_id)

    try:
        while True:
            raw = await websocket.receive_text()
            async with async_session() as db:
                await handle_ws_message(websocket, user_id, raw, db)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@app.get("/health")
async def health():
    return {"status": "ok"}
