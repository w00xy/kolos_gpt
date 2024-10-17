import datetime

from sqlalchemy import String, BigInteger, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="user")


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[Text] = mapped_column(Text, nullable=False)
    tokens: Mapped[Integer] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="messages")
