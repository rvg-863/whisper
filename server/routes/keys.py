import uuid

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.deps import get_current_user
from server.models.user import User

router = APIRouter(prefix="/auth/keys", tags=["keys"])


class PrekeysUpload(BaseModel):
    prekeys: list[str]


class PrekeyBundle(BaseModel):
    identity_key_public: str | None
    signed_prekey_public: str | None
    signed_prekey_signature: str | None
    one_time_prekey: str | None


@router.post("/prekeys")
async def upload_prekeys(
    body: PrekeysUpload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = user.one_time_prekeys or []
    existing.extend(body.prekeys)
    user.one_time_prekeys = existing
    await db.commit()
    return {"count": len(existing)}


@router.get("/bundle/{user_id}", response_model=PrekeyBundle)
async def get_prekey_bundle(
    user_id: uuid.UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    one_time_prekey = None
    if target.one_time_prekeys:
        one_time_prekey = target.one_time_prekeys.pop(0)
        await db.commit()

    return PrekeyBundle(
        identity_key_public=target.identity_key_public,
        signed_prekey_public=target.signed_prekey_public,
        signed_prekey_signature=target.signed_prekey_signature,
        one_time_prekey=one_time_prekey,
    )
