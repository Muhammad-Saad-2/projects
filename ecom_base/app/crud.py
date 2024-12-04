from sqlalchemy.orm import Session
from app.models import User
from app.utils import get_password_hash

def create_user(db:Session, email: str, password:str):
    hashed_password = get_password_hash(password) #hash the plain text password
    user = User(email = email, hashed_password = hashed_password) #Create a new User Object
    db.add(user) #add the user to the session
    db.commit()  #commit the session
    db.refresh(user) #refresh to load the new user's ID 
    return user  #return the newly created user 