from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    

# hashed = hash_password("wassupnigga")

# verified_password =verify_password("wassupnigga", hashed)
# if verified_password == True:
#     print("validated")
# else:
#     print("can't validate")
