import uuid
from sqlalchemy import create_engine, ForeignKey, select, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base, DeclarativeBase, Mapped, mapped_column, relationship
from src.db import Base
from src.models.ChatModel import Chat


class User(Base):
   __tablename__ ="user"
   id:Mapped[int] = mapped_column(primary_key=True)
   username:Mapped[str] = mapped_column(String, nullable=False, unique=True)
   password: Mapped[bytes] = mapped_column(nullable=False)
   chats:Mapped[list["Chat"]] = relationship(uselist=True, back_populates="users", secondary="users_chats")


class UserChat(Base):
   __tablename__ = "users_chats"
   user_id:Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
   chat_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("chat.chat_id"), primary_key=True)