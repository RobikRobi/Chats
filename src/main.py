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


@app.get("/create-data")
async def get_data(session:AsyncSession = Depends(get_session)):

    user = User(username = "admin1", password ="1234")
    user2 = User(username = "admin12", password ="122334")
    user3 = User(username = "admin123", password ="1232334")
    chat1 = Chat(chat_id = uuid.uuid4())
    chat2 = Chat(chat_id = uuid.uuid4())
    chat1.users.append(user)
    chat1.users.append(user2)
    chat2.users.append(user3)
    chat2.users.append(user2)
    session.add_all([chat1,chat2])
    session.commit()
    
    return 200