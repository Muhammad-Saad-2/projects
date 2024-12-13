from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#cryptographic context for password sharing 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(password: str)-> str:
    return pwd_context.hash(password)

#function to verify password 
def verify_password(plain_password: str, hashed_password:str)-> bool:
    return pwd_context.verify(plain_password, hashed_password)

#function to create the access token
def create_access_token(data:dict)->str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)  
    to_encode.update({"exp": expire}) #add expiration time to the  token 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM) #generate the token 
    return encoded_jwt