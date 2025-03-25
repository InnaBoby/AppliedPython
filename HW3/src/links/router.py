from fastapi import APIRouter, Depends, HTTPException, status
import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.db import get_async_session, User, Link
from src.auth.auth_backend import current_active_user
from sqlalchemy import select, insert, delete, update, and_
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi_cache.decorator import cache
import time


router = APIRouter (
    prefix='/links',
    tags=['Links']
)

characters = string.ascii_letters + string.digits

@router.post('/shorten')
async def create_short_link(link: str, session: AsyncSession=Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        short_link = ''.join(random.choices(characters, k=6))
        # проверяем, чтобы short_link не было в БД
        statement = select(Link).filter(Link.short_link == short_link)
        unique_short_link = await session.execute(statement)
        while not unique_short_link:
            short_link = ''.join(random.choices(characters, k=6))
        #проверяем список текущих ссылок пользователя
        statement = select(Link.link).where(Link.user_id==user.id)
        current_links = await session.execute(statement)
        current_links = current_links.scalars().all()
        if link not in current_links:
            # добавляем в БД новую ссылку
            statement = insert(Link).values(user_id=user.id, link=link, short_link=short_link, number_of_clics=0)
            await session.execute(statement)
            await session.commit()
            return {
                'status' : 'success',
                'data' : short_link
            }
        else:
            # если у пользователя уже есть эта ссылка, напоминаем ее short_link
            statement = select(Link.short_link).where(and_(Link.user_id == user.id, Link.link == link))
            short = await session.execute(statement)
            short = short.scalar()
            return f"For {link} exist short link {short}"

    except Exception as e:
        raise HTTPException (status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail = e)


@router.get('/{short_link}')
@cache(expire=60)
async def redirect(short_link: str, session: AsyncSession=Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        query = select(Link.link).where(and_(Link.short_link == short_link, Link.user_id==user.id))
        url = await session.execute(query)
        url = url.scalar_one_or_none()
        if url is None:
            raise HTTPException(status_code=404,
                                detail="Short link not found")
        statement = select(Link.number_of_clics).where(and_(Link.short_link == short_link, Link.user_id==user.id))
        current_clics = await session.execute(statement)
        current_clics = current_clics.scalar_one_or_none()
        statement = update(Link).where(and_(Link.short_link == short_link, Link.user_id==user.id)).values(number_of_clics=current_clics+1)
        await session.execute(statement)
        await session.commit()

        return RedirectResponse(url=url)

    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail = e)


@router.delete('/{short_link}')
async def delete_link (short_link: str, user: User = Depends(current_active_user), session: AsyncSession=Depends(get_async_session)):
    if user.is_active:
        query = delete(Link).where(and_(Link.short_link == short_link, Link.user_id==user.id))
        await session.execute(query)
        await session.commit()
        return {"message": f"Short link '{short_link}' successfully deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only a registered user can delete links!'
                            )

@router.put('/{short_link}')
async def update_short_link(long_link: str, user: User = Depends(current_active_user), session: AsyncSession=Depends(get_async_session)):
    if user.is_active:
        new_short_link = ''.join(random.choices(characters, k=6))
        #проверяем, чтобы new_short_link не было в БД
        statement = select(Link).filter(Link.short_link == new_short_link)
        unique_short_link = await session.execute(statement)
        while  not unique_short_link:
            new_short_link = ''.join(random.choices(characters, k=6))
        try:
            statement = (update(Link)
                         .where(and_(Link.user_id == user.id, Link.link == long_link))
                         .values(short_link=new_short_link))
            await session.execute(statement)
            await session.commit()
            return {'message' : f"New short-link {new_short_link} for {long_link}"}
        except:
            raise HTTPException(status_code=404,
                                detail="Link not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only a registered user can update links!")



@router.get('/{short_link}/stats')
@cache(expire=60)
async def short_link_info(short_link: str, session: AsyncSession=Depends(get_async_session), user: User = Depends(current_active_user)):
    try:
        statement = select(Link.link).where(and_(Link.user_id == user.id, Link.short_link == short_link))
        original_link = await session.execute(statement)
        original_link = original_link.scalar()
        statement = select(Link.number_of_clics).where(and_(Link.user_id == user.id, Link.short_link == short_link))
        clicks = await session.execute(statement)
        clicks = clicks.scalar()
        statement = select(Link.created_at).where(and_(Link.user_id == user.id, Link.short_link == short_link))
        create_date = await session.execute(statement)
        create_date = create_date.scalar()
        return {
            'Original URL' : original_link,
            'number of clicks' : clicks,
            'created_at' : create_date
        }
    except:
        raise HTTPException(status_code=404,
                            detail="Short link not found")


#Хэндлер с алиасом (как поняла, нужно добавить к короткой ссылке префикс, введенный пользователем)
class AliasLink(BaseModel):
    link: str
    alias: str

@router.post('/alias')
async def short_link_with_alias(alias: AliasLink,
                                session: AsyncSession=Depends(get_async_session),
                                user: User = Depends(current_active_user)):
    try:
        short_link = f'{alias.alias}_'+''.join(random.choices(characters, k=6))
        # проверяем, чтобы short_link не было в БД
        statement = select(Link).filter(Link.short_link == short_link)
        unique_short_link = await session.execute(statement)
        while not unique_short_link:
            short_link = f'{alias.alias}_'+''.join(random.choices(characters, k=6))
        # проверяем список текущих ссылок пользователя
        statement = select(Link.link).where(Link.user_id == user.id)
        current_links = await session.execute(statement)
        current_links = current_links.scalars().all()
        if alias.link not in current_links:
            # добавляем в БД новую ссылку
            statement = insert(Link).values(user_id=user.id, link=alias.link, short_link=short_link, number_of_clics=0)
            await session.execute(statement)
            await session.commit()
            return {
                'status': 'success',
                'data': short_link
            }
        else:
            # если у пользователя уже есть эта ссылка, напоминаем ее short_link
            statement = select(Link.short_link).where(and_(Link.user_id == user.id, Link.link == alias.link))
            short = await session.execute(statement)
            short = short.scalar()
            return f"For {alias.link} exist short link {short}"
    except Exception as e:
        raise HTTPException (status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail = e)


@router.get('/search/')
async def search(original_url : str,
                 session: AsyncSession = Depends(get_async_session),
                 user: User = Depends(current_active_user)):
    if not original_url:
        return {"error": "Required original_url"}
    statement = select(Link.short_link).where(and_(Link.user_id == user.id, Link.link == original_url))
    short = await session.execute(statement)
    short = short.scalar()
    return f"For {original_url} exist short link {short}"


# @router.post('/lifetime')
# async def lifetime (short_link: str,
#                     date: datetime,
#                     session: AsyncSession = Depends(get_async_session),
#                     user: User = Depends(current_active_user)):
#     if user.is_active:
#         statement = update(Link).where(and_(Link.short_link == short_link, Link.user_id == user.id)).values(
#             expires_at=date)
#         await session.execute(statement)
#         await session.commit()
#         return {'message' : f'{short_link} will active before {date}'}


@router.get('/long/')
@cache(expire=60)
async def long_operation(session: AsyncSession = Depends(get_async_session)):
    if session:
        time.sleep(10)
    return 'Long operation complete!'

