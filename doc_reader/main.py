from browser_use.llm import ChatGoogle
from browser_use import Agent
from dotenv import load_dotenv
import os
from browser_use import Agent
import asyncio

# Read GOOGLE_API_KEY into env
load_dotenv()

api_key: str = os.getenv("GOOGLE_API_KEY", "" )
print(api_key)
model = "gemini-2.5-flash"



#Initialize the model
llm = ChatGoogle(
    model = model,
    api_key = api_key
)


async def main():
    agent = Agent(
        task="seach for the fastapi documentation and search for the topics Response header there",
        llm=llm,
    )
    result = await agent.run()
    print(result.final_result)

asyncio.run(main())