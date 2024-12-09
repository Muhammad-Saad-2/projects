from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import schemas, crud, models, database

#initalize fastapi app 
app = FastAPI()

#creating database tables 
models.Base.metadata.create_all(bind = database.engine)

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    #check if the email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    #Create new user 
    new_user = crud.create_user(db, email=user.email, password= user.password)
    return new_user
