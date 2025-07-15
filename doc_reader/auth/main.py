from typing import Annotated
from shared.databases.postgres_conn import create_engine, get_session
from auth.app.models.base  import get_base, User
from fastapi import FastAPI, Depends
from auth.app.schemas.user_schemas import UserCreate
from sqlmodel import Session
from contextlib import asynccontextmanager


base = get_base()
SessionDep = Annotated[Session, Depends(get_session)]
engine = create_engine()

@asynccontextmanager
def create_tables():
    try:
        with engine.begin() as conn:
            conn.run_sync(base.metadata.create_all)
    except Exception as e:
        print(e)
    finally:
        conn.close()


app: FastAPI = FastAPI()



@app.post("/register", response_model = UserCreate)
async def register_user(
    user: User,
    session: Session,
):
    existing_user = session.exec(User)

    
    







# from browser_use.llm import ChatGoogle
# from browser_use import Agent
# from dotenv import load_dotenv
# import os
# from browser_use import Agent
# import asyncio

# # Read GOOGLE_API_KEY into env
# load_dotenv()

# api_key: str = os.getenv("GOOGLE_API_KEY", "" )
# print(api_key)
# model = "gemini-2.5-flash"



# #Initialize the model
# llm = ChatGoogle(
#     model = model,
#     api_key = api_key
# )


# async def main():
#     agent = Agent(
#         task="seach for the fastapi documentation and search for the topics Response header there",
#         llm=llm,
#     )
#     result = await agent.run()
#     print(result.final_result)

# asyncio.run(main())


numbers = [1,3,5,2,4,6,10,8,9]


length = len(numbers) + 1

present_numbers = set(numbers)

for i in range(1, length):
    if i not in present_numbers:
        numbers.append(i)
        print(i)
        numbers.sort()
        print(numbers)







    
