from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.db import get_async_session, Link, User
from src.auth.auth_backend import current_active_user
from datetime import datetime
from sqlalchemy import update, and_
from src.tasks.tasks import clean_expired_links

router = APIRouter (
    prefix='/links',
    tags=['Links']
)


@router.post('/lifetime')
async def lifetime (short_link: str,
                    date: datetime,
                    session: AsyncSession = Depends(get_async_session),
                    user: User = Depends(current_active_user)):
    if user.is_active:
        statement = update(Link).where(and_(Link.short_link == short_link, Link.user_id == user.id)).values(
            expires_at=date)
        await session.execute(statement)
        await session.commit()

        clean_expired_links.apply_async()

        return {'message' : f'{short_link} will active before {date}'}