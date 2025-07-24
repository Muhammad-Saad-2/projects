from passlib.context import CryptContext
import re
from pydantic import EmailStr
from password_strength import PasswordPolicy
import random
from fastapi.responses import JSONResponse



def is_valid_email_regex(email: EmailStr):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def generate_otp():
    one_time_password = " "
    for _ in range(6):
        one_time_password += str(random.randrange(0, 9))
    return one_time_password




'''create password policy to include the attirbutes so that the password can not be breaached '''

policy = PasswordPolicy.from_names(
    uppercase = 1,
    numbers = 1,
    special =1 ,
    length = 8,
)

def run_password_policy(password:str):

    failed_rules = policy.test(password)
    if not failed_rules:
        return password is not None
    


pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


    



