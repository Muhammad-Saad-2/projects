from typing import Annotated
from shared.databases.postgres_conn import async_engine, get_async_session, create_table
from auth.app.models.base  import get_base, User
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from auth.app.schemas.user_schemas import UserCreate, UserLogin
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import asyncio
from auth.app.services.utilities import hash_password, is_valid_email_regex, run_password_policy, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from auth.app.routers.auth_router import router

base = get_base()
engine = async_engine 
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


# async def create_tables():
#     try:
#         async with engine.begin() as conn:
#             await conn.run_sync(base.metadata.create_all)
#     finally:
#         await conn.close()



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("creating database tables")
    await create_table()
    print("tables created")
    yield
    

app = FastAPI(
    title="Auth utility",
    lifespan=lifespan
)

app.include_router(router)


# @app.post("/sign_up/", response_model = User)
# async def register_user(
#     user: UserCreate,
#     session: SessionDep,
# ):
#     query = select(User).where(User.email == user.email)
#     existing_user_result = await session.execute(query)  #scalar() method is only called on executed object
#     existing_user = existing_user_result.scalars().first()
#     if not existing_user:
#         regex_check_on_email = is_valid_email_regex(user.email)
#         if not regex_check_on_email:
#             raise HTTPException(status_code=401,detail="Invalid Email Pattern")
#         password_policy = run_password_policy(user.password)
#         if not password_policy:
            
#             raise HTTPException(status_code=401,detail="the password must contain atleast one uppercase, number and a special character")
       
#         password = hash_password(user.password)
#         db_user = User(
#             username = user.username,
#             email=user.email,
#             hashed_password=password
#         )
#         session.add(db_user)
#         await session.commit()
#         await session.refresh(db_user)
#         print("your account has been registered")
#         return db_user
    
#     else:
#         raise HTTPException(status_code=401, detail="user already registered")


# @app.post("/login/")
# async def login(
#     user: UserLogin,
#     session: SessionDep
# ):
#     query= select(User).where(User.email == user.email)
#     registered_user_result = await session.execute(query)
#     registered_user = registered_user_result.scalars().first()
#     if not registered_user:
#         raise HTTPException(status_code = 401, detail = "unauthorized access, please regsiter yourself first")
#     user_password = user.password
#     db_password_query = session.execute(select(User)).where(User.hashed_password)
#     db_password = db_password_query.scalars().first()
#     password_match =verify_password(user_password, db_password)
#     if not password_match:
#         raise HTTPException(status_code= 401, detail= "incorrect password")
#     else:
#         return {"message" : "user logged in"}
    
    
    







# # from browser_use.llm import ChatGoogle
# # from browser_use import Agent
# # from dotenv import load_dotenv
# # import os
# # from browser_use import Agent
# # import asyncio

# # # Read GOOGLE_API_KEY into env
# # load_dotenv()

# # api_key: str = os.getenv("GOOGLE_API_KEY", "" )
# # print(api_key)
# # model = "gemini-2.5-flash"



# # #Initialize the model
# # llm = ChatGoogle(
# #     model = model,
# #     api_key = api_key
# # )


# # async def main():
# #     agent = Agent(
# #         task="seach for the fastapi documentation and search for the topics Response header there",
# #         llm=llm,
# #     )
# #     result = await agent.run()
# #     print(result.final_result)

# # asyncio.run(main())


# # numbers = [1,3,5,2,4,6,10,8,9]


# # length = len(numbers) + 1

# # present_numbers = set(numbers)

# # for i in range(1, length):
# #     if i not in present_numbers:
# #         numbers.append(i)
# #         print(i)
# #         numbers.sort()
# #         print(numbers)






    
