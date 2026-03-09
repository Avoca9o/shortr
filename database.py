import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models import Base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Link, User
from sqlalchemy import select, delete

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def close_db():
    await engine.dispose()

async def add_link_db(db:AsyncSession, original_url: str, short_url: str, expires_at: datetime, user_id):
    link = Link(original_url=original_url, short_url=short_url, expires_at=expires_at, user_id=user_id)
    db.add(link)
    await db.commit()
    return link

async def get_link_db(db:AsyncSession, short_url: str):
    result = await db.execute(select(Link).where(Link.short_url == short_url))
    return result.scalar_one_or_none()

async def delete_link_without_user_db(db:AsyncSession, short_url: str):
    await db.execute(delete(Link).where(Link.short_url == short_url, Link.user_id == None))
    await db.commit()

async def delete_link_db(db:AsyncSession, current_user: int, short_url: str):
    await db.execute(delete(Link).where(Link.short_url == short_url, Link.user_id == current_user))
    await db.commit()

async def update_link_db(db:AsyncSession, current_user: int, short_url: str, url: str):
    result = await db.execute(select(Link).where(Link.short_url == short_url, Link.user_id == current_user))
    link = result.scalar_one_or_none()
    if not link:
        raise ValueError("Link not found")
    link.original_url = url
    link.access_count += 1
    await db.commit()
    await db.refresh(link)

async def increase_link_access_count_db(db:AsyncSession, short_url: str):
    result = await db.execute(select(Link).where(Link.short_url == short_url))
    link = result.scalar_one_or_none()
    if not link:
        raise ValueError("Link not found")
    link.access_count += 1
    await db.commit()
    await db.refresh(link)

async def get_link_by_original_url_db(db:AsyncSession, original_url: str):
    query = select(Link).where(Link.original_url == original_url)
    result = await db.execute(query)
    link = result.scalars().first()
    return link

async def create_user_db(db:AsyncSession, username: str, password: str):
    user = User(username=username, hashed_password=str(password))
    db.add(user)
    await db.commit()
    return user

async def get_user_by_username_db(db:AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()
    return user

async def get_top_10_links_db(db:AsyncSession):
    query = select(Link).order_by(Link.access_count.desc()).limit(10)
    result = await db.execute(query)
    links = result.scalars().all()
    return [
        {
            "short_url": link.short_url,
            "original_url": link.original_url,
            "access_count": link.access_count
        }
        for link in links
    ]
