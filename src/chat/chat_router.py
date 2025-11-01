from fastapi import APIRouter, Depends, status, Path, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid

from src.chat.WebsocetConnect import ConnectionManager
from src.models.UserModel import User, UserChat
from src.models.ChatModel import Chat, Message
from src.db import get_session
from src.get_current_user import get_current_user

app = APIRouter(prefix="/chats", tags=["Chats"])

channels = ConnectionManager()


@app.post("/add_chat")
async def add_caht(session:AsyncSession = Depends(get_session)):
    chat_id = uuid.uuid4()
    chat = Chat(chat_id = chat_id)
    session.add(chat)
    await session.commit()
    return chat_id

@app.post("/{chat_id}/join")
async def join_chat(chat_id: uuid.UUID = Path(...), 
                    current_user: User = Depends(get_current_user), 
                    session: AsyncSession = Depends(get_session)):
   chat_result = await session.execute(select(Chat).where(Chat.chat_id == chat_id))
   if not chat_result:
      raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} not found")
   user_chat_result = await session.execute(
      select(UserChat).where(
         UserChat.user_id == current_user.id, 
         UserChat.chat_id == chat_id))
   user_chat = user_chat_result.scalar_one_or_none()
   
   if user_chat:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in this chat"
        )
   new_user_chat = UserChat(user_id = current_user.id, chat_id = chat_id)
   session.add(new_user_chat)
   await session.commit()
   return {
        "message": f"User {current_user.username} successfully joined chat {chat_id}",
        "chat_id": str(chat_id),
        "user_id": current_user.id
    }

@app.get("/chat/{chat_id}")
async def get_chat(chat_id: uuid.UUID, session:AsyncSession = Depends(get_session)):
   stmt = select(Chat).where(Chat.chat_id == chat_id).options(selectinload(Chat.users))
   chat = await session.scalar(stmt)
   if not chat:
      raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} not found")
   return chat



@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id:uuid.UUID, session:AsyncSession = Depends(get_session)):
    chat = await session.scalar(select(Chat).options(selectinload(Chat.messages)).where(Chat.chat_id == chat_id))
    print(chat.chat_id)
    if not chat:
       await websocket.close()
       return
    await channels.connect(websocket, chat_id, 1)
    data = []
    for message in chat.messages:
     data.append(message.message)
    print(data)

    await websocket.send_json(data  )
    print(websocket.headers)
    try:
        while True:

            data = await websocket.receive_text()
            with session() as ses:
               message = Message(message= data, chat_id = chat_id)
               ses.add(message)
               ses.commit()
            await channels.broadcast(chat_id, data)

    except WebSocketDisconnect:
        print("Client disconnected")


