from shared.config.settings import get_settings
from shared.models.base import get_base
import redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pymongo.server_api import ServerApi
from pymongo import AsyncMongoClient
import asyncio

settings = get_settings()
base = get_base()

'''Esatablish connection with redis'''
r = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    decode_responses=True,
    username = settings.REDIS_USERNAME,
    password = settings.REDIS_PASSWORD
    
)

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


async def create_table():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
    except Exception as e:
         print(e)
    finally:
         conn.close()

asyncio.run(create_table())




'''Establish connection with mongodb'''
async def connect_mongo():
        mongodb = AsyncMongoClient(settings.MONGODB_URL, server_api = ServerApi(
            version= '1', strict=True, deprecation_errors=True
        ))



        try:
            await mongodb.admin.command({'ping': 1})
            print("pinged your deployment")
        except Exception as e:
            print(e)
        finally:
             await mongodb.close()

asyncio.run (connect_mongo())