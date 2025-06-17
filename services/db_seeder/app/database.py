from config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine(settings.DATABASE_URL, echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)
