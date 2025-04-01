from celery import Celery
from src.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from fastapi import Depends
from src.auth.db import get_async_session, Link
from sqlalchemy import select, delete
from datetime import datetime


celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(default_retry_delay=5, max_retries=2)
async def clean_expired_links():
    try:
        session = Depends(get_async_session)
        links = await session.execute(select(Link))
        links = links.scalars().all()
        for link in links:
            if datetime.now() > link.expires_at:
                await session.execute(delete(link))
                await session.commit()
    except:
        clean_expired_links.retry()

