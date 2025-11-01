import uuid
from fastapi import FastAPI, Depends
from binascii import Error
from src.db import engine, Base
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from src.models.UserModel import User
from src.models.ChatModel import Chat
from src.auth.auth_utilits import create_access_token
from src.auth.auth_router import app as auth_app
from src.chat.chat_router import app as chat_app


app = FastAPI()

app.include_router(auth_app)
app.include_router(chat_app)

@app.get("/init")
async def create_db():
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except Error as e:
            print(e)     
        await  conn.run_sync(Base.metadata.create_all)
    return({"msg":"db creat! =)"})
