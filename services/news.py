from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists, delete, and_

from .. import models, schemas


async def create_news(db_session: AsyncSession, data: schemas.NewsInDB) -> models.News:
    db_obj = models.News(**data.model_dump(exclude_unset=True))

    db_session.add(db_obj)
    await db_session.commit()
    await db_session.refresh(db_obj)

    return db_obj


async def get_news_by_url(db_session: AsyncSession, news_url: str) -> models.News | None:
    stmt = select(models.News).where(models.News.news_url == news_url)
    news: models.News | None = (await db_session.execute(stmt)).scalar()
    return news
    