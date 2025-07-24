import redis
from shared.config.settings import get_settings
 

settings = get_settings()

'''Esatablish connection with redis'''
redis_client = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    decode_responses=True,
    username = settings.REDIS_USERNAME,
    password = settings.REDIS_PASSWORD
    
)
