import uuid
from typing import Optional

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.deps import get_current_user
from server.models.user import User
from server.models.channel import Channel, ChannelType
from server.models.server_member import ServerMember
from server.models.message import Message

router = APIRouter(prefix="/channels", tags=["channels"])


class CreateChannelRequest(BaseModel):
    server_id: str
    name: str = Field(min_length=1, max_length=64)
    type: ChannelType = ChannelType.TEXT


class ChannelResponse(BaseModel):
    id: str
    server_id: str
    name: str
    type: str


async def verify_membership(user_id: uuid.UUID, server_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(
        select(ServerMember).where(ServerMember.user_id == user_id, ServerMember.server_id == server_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this server")
    return member


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    body: CreateChannelRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    server_id = uuid.UUID(body.server_id)
    await verify_membership(user.id, server_id, db)

    channel = Channel(server_id=server_id, name=body.name, type=body.type)
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return ChannelResponse(id=str(channel.id), server_id=str(channel.server_id), name=channel.name, type=channel.type.value)


@router.get("/by-server/{server_id}", response_model=list[ChannelResponse])
async def list_channels(
    server_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await verify_membership(user.id, server_id, db)

    result = await db.execute(select(Channel).where(Channel.server_id == server_id))
    channels = result.scalars().all()
    return [ChannelResponse(id=str(c.id), server_id=str(c.server_id), name=c.name, type=c.type.value) for c in channels]


class MessageResponse(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    sender_username: str
    content: str
    created_at: str


@router.get("/{channel_id}/messages", response_model=list[MessageResponse])
async def get_channel_messages(
    channel_id: uuid.UUID,
    before: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get channel and verify membership
    ch_result = await db.execute(select(Channel).where(Channel.id == channel_id))
    channel = ch_result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    await verify_membership(user.id, channel.server_id, db)

    query = (
        select(Message, User.username)
        .join(User, User.id == Message.sender_id)
        .where(Message.channel_id == channel_id)
    )
    if before:
        query = query.where(Message.created_at < before)
    query = query.order_by(Message.created_at.desc()).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return [
        MessageResponse(
            id=str(msg.id),
            channel_id=str(msg.channel_id),
            sender_id=str(msg.sender_id),
            sender_username=username,
            content=msg.ciphertext,
            created_at=msg.created_at.isoformat(),
        )
        for msg, username in reversed(rows)
    ]
