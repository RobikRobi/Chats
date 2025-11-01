import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.UserModel import User

class Chat(Base):
   __tablename__ = "chat"
   chat_id:Mapped[uuid.UUID] = mapped_column(unique=True, primary_key=True)
   users:Mapped[list["User"]] = relationship(uselist=True, back_populates="chats", secondary="users_chats")
   messages:Mapped[list["Message"]] = relationship(uselist=True)


class Message(Base):
    __tablename__="message"
    id:Mapped[int] = mapped_column(primary_key=True)
    message:Mapped[str]
    chat_id:Mapped[uuid.UUID]  = mapped_column(ForeignKey("chat.chat_id"))
