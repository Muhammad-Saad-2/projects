from shared.config.settings import get_settings
from auth.app.models.base import get_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import asyncio


settings = get_settings()
base = get_base()


'''Establish connection with postgres'''
POSTGRES_URL = settings.POSTGRES_URL


async_engine = create_async_engine(
    POSTGRES_URL,
    echo = True,
    connect_args = {
        'ssl': True
    }
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    autoflush= True,
    expire_on_commit=False
)


    
# async def create_table():
#     try:
#         with async_engine.begin() as conn:
#             await conn.run_sync(base.metadata.create_all)
#     except Exception as e:
#          print(e)
#     finally:
#          conn.close()



# '''dependency to get database function'''
# def get_session():
#     pg = AsyncSessionLocal()
#     try:
#         yield pg
#     finally:
#         pg.close()


