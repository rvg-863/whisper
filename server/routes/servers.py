import secrets
import uuid

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.deps import get_current_user
from server.models.user import User
from server.models.server import Server
from server.models.channel import Channel, ChannelType
from server.models.server_member import ServerMember, MemberRole

router = APIRouter(prefix="/servers", tags=["servers"])


class CreateServerRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class JoinServerRequest(BaseModel):
    invite_code: str


class ServerResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    invite_code: str


class MemberResponse(BaseModel):
    user_id: str
    username: str
    role: str


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    body: CreateServerRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    server = Server(
        name=body.name,
        owner_id=user.id,
        invite_code=secrets.token_urlsafe(8),
    )
    db.add(server)
    await db.flush()

    # Add owner as member
    db.add(ServerMember(user_id=user.id, server_id=server.id, role=MemberRole.OWNER))

    # Create default #general channel
    db.add(Channel(server_id=server.id, name="general", type=ChannelType.TEXT))

    await db.commit()
    await db.refresh(server)
    return ServerResponse(id=str(server.id), name=server.name, owner_id=str(server.owner_id), invite_code=server.invite_code)


@router.get("", response_model=list[ServerResponse])
async def list_servers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Server)
        .join(ServerMember, ServerMember.server_id == Server.id)
        .where(ServerMember.user_id == user.id)
    )
    servers = result.scalars().all()
    return [ServerResponse(id=str(s.id), name=s.name, owner_id=str(s.owner_id), invite_code=s.invite_code) for s in servers]


@router.post("/join", response_model=ServerResponse)
async def join_server(
    body: JoinServerRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Server).where(Server.invite_code == body.invite_code))
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code")

    # Check if already a member
    existing = await db.execute(
        select(ServerMember).where(ServerMember.user_id == user.id, ServerMember.server_id == server.id)
    )
    if existing.scalar_one_or_none():
        return ServerResponse(id=str(server.id), name=server.name, owner_id=str(server.owner_id), invite_code=server.invite_code)

    db.add(ServerMember(user_id=user.id, server_id=server.id, role=MemberRole.MEMBER))
    await db.commit()
    return ServerResponse(id=str(server.id), name=server.name, owner_id=str(server.owner_id), invite_code=server.invite_code)


@router.get("/{server_id}/members", response_model=list[MemberResponse])
async def list_members(
    server_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify user is a member
    membership = await db.execute(
        select(ServerMember).where(ServerMember.user_id == user.id, ServerMember.server_id == server_id)
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    from server.models.user import User as UserModel
    result = await db.execute(
        select(ServerMember, UserModel.username)
        .join(UserModel, UserModel.id == ServerMember.user_id)
        .where(ServerMember.server_id == server_id)
    )
    rows = result.all()
    return [MemberResponse(user_id=str(m.user_id), username=username, role=m.role.value) for m, username in rows]
