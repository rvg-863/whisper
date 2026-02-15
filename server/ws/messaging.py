import json
import uuid

from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.ws.manager import manager
from server.models.server_member import ServerMember
from server.models.channel import Channel


async def handle_ws_message(websocket: WebSocket, user_id: uuid.UUID, raw: str, db: AsyncSession):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"type": "error", "detail": "Invalid JSON"}))
        return

    msg_type = data.get("type")

    if msg_type == "join_channel":
        channel_id = data.get("channel_id")
        if not channel_id:
            return

        # Verify membership in the channel's server
        result = await db.execute(select(Channel).where(Channel.id == uuid.UUID(channel_id)))
        channel = result.scalar_one_or_none()
        if not channel:
            return

        membership = await db.execute(
            select(ServerMember).where(
                ServerMember.user_id == user_id,
                ServerMember.server_id == channel.server_id,
            )
        )
        if not membership.scalar_one_or_none():
            return

        room_id = f"channel:{channel_id}"
        manager.join_room(room_id, user_id)
        await websocket.send_text(json.dumps({"type": "joined", "channel_id": channel_id}))

    elif msg_type == "leave_channel":
        channel_id = data.get("channel_id")
        if channel_id:
            manager.leave_room(f"channel:{channel_id}", user_id)

    elif msg_type == "message":
        channel_id = data.get("channel_id")
        content = data.get("content")
        if not channel_id or not content:
            return

        room_id = f"channel:{channel_id}"
        if user_id not in manager.rooms.get(room_id, set()):
            return

        # Import here to avoid circular imports
        from server.models.message import Message
        from server.models.user import User

        # Get username
        user_result = await db.execute(select(User.username).where(User.id == user_id))
        username = user_result.scalar_one()

        msg = Message(
            channel_id=uuid.UUID(channel_id),
            sender_id=user_id,
            ciphertext=content,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)

        broadcast = {
            "type": "message",
            "id": str(msg.id),
            "channel_id": channel_id,
            "sender_id": str(user_id),
            "sender_username": username,
            "content": content,
            "created_at": msg.created_at.isoformat(),
        }
        await manager.broadcast_to_room(room_id, broadcast)

    elif msg_type == "join_dm":
        conversation_id = data.get("conversation_id")
        if conversation_id:
            room_id = f"dm:{conversation_id}"
            manager.join_room(room_id, user_id)
            await websocket.send_text(json.dumps({"type": "joined_dm", "conversation_id": conversation_id}))

    elif msg_type == "leave_dm":
        conversation_id = data.get("conversation_id")
        if conversation_id:
            manager.leave_room(f"dm:{conversation_id}", user_id)

    elif msg_type == "dm_message":
        conversation_id = data.get("conversation_id")
        content = data.get("content")
        if not conversation_id or not content:
            return

        room_id = f"dm:{conversation_id}"
        if user_id not in manager.rooms.get(room_id, set()):
            return

        from server.models.message import Message
        from server.models.user import User

        user_result = await db.execute(select(User.username).where(User.id == user_id))
        username = user_result.scalar_one()

        msg = Message(
            conversation_id=uuid.UUID(conversation_id),
            sender_id=user_id,
            ciphertext=content,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)

        broadcast = {
            "type": "dm_message",
            "id": str(msg.id),
            "conversation_id": conversation_id,
            "sender_id": str(user_id),
            "sender_username": username,
            "content": content,
            "created_at": msg.created_at.isoformat(),
        }
        await manager.broadcast_to_room(room_id, broadcast)
