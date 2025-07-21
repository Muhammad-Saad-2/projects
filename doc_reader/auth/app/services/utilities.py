from passlib.context import CryptContext
import re
from pydantic import EmailStr

pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    




def is_valid_email_regex(email: EmailStr):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return re.match(regex, email) is not None

my_email = is_valid_email_regex("saadjameel2001@gmail.com")
if my_email == True:
    print("yes")
else:
    print("no")
