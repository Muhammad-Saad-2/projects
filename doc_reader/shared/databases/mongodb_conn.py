from pymongo.server_api import ServerApi
from pymongo import AsyncMongoClient
from shared.config.settings import get_settings
import asyncio 

settings = get_settings()

'''Establish connection with mongodb'''
async def connect_mongo():
        mongodb = AsyncMongoClient(settings.MONGODB_URL, server_api = ServerApi(
            version= '1', 
            strict=True, 
            deprecation_errors=True
        ))

        try:
            await mongodb.admin.command({'ping': 1})
            print("pinged your deployment")
        except Exception as e:
            print(e)
        finally:
             await mongodb.close()

asyncio.run(connect_mongo())
