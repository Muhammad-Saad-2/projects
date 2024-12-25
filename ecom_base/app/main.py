from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import schemas, crud, models, database, utils 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.schemas import Token

#initalize fastapi app 
app = FastAPI()

#creating database tables 
models.Base.metadata.create_all(bind = database.engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    #check if the email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    #Create new user 
    new_user = crud.create_user(db, email=user.email, password= user.password)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_user(form_data : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(database.get_db) ):
    #find the user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail= " invalid email or password ")
    
    #verifying the password
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail= " invalid email or password")
    
    #creating the token 
    access_token = utils.create_access_token(data= {"sub": user.email, "role": user.role})
    return{"access_token": access_token, "token_type": "bearer"}


@app.get("/protected-route")
def protected_route(token:str = Depends(oauth2_scheme)):

    token_data = utils.verify_token(token)
    return {"message": "you are autheticated", "token_data": token_data }