from passlib.context import CryptContext
import re
from pydantic import EmailStr
from password_strength import PasswordPolicy


pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

def is_valid_email_regex(email: EmailStr):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None


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

    # if not failed_rules:
    #     print(f"the password must contain atleast one uppercase, one number and one special character ")
    # else:
    #     print(f"the password : {password} is invalid as per fromat")
    


def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    



def check_password_function():
    password = "iampassword"
    hashed_password_form = hash_password(password)
    verified_password = verify_password(password, hashed_password_form)

    if not verified_password:
        print("No")
    else:
        print("Yes")


check_password_function()