import redis
from shared.config.settings import Settings


settings = Settings()

'''Esatablish connection with redis'''
r = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    decode_responses=True,
    username = settings.REDIS_USERNAME,
    password = settings.REDIS_PASSWORD
    
)
