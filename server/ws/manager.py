import json
import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # user_id -> set of websockets (multi-device)
        self.active_connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        # room_id -> set of user_ids
        self.rooms: dict[str, set[uuid.UUID]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        await websocket.accept()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: uuid.UUID):
        self.active_connections[user_id].discard(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]
            # Remove from all rooms
            for room_members in self.rooms.values():
                room_members.discard(user_id)

    def join_room(self, room_id: str, user_id: uuid.UUID):
        self.rooms[room_id].add(user_id)

    def leave_room(self, room_id: str, user_id: uuid.UUID):
        self.rooms[room_id].discard(user_id)
        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def send_personal(self, user_id: uuid.UUID, message: dict):
        data = json.dumps(message)
        dead = []
        for ws in self.active_connections.get(user_id, set()):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections[user_id].discard(ws)

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: uuid.UUID | None = None):
        data = json.dumps(message)
        for user_id in list(self.rooms.get(room_id, set())):
            if user_id == exclude:
                continue
            dead = []
            for ws in self.active_connections.get(user_id, set()):
                try:
                    await ws.send_text(data)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.active_connections[user_id].discard(ws)


manager = ConnectionManager()
