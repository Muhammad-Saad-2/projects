from passlib.context import CryptContext

#cryptographic context for password sharing 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(password: str)-> str:
    return pwd_context.hash(password)