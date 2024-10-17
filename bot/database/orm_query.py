from typing import List, Tuple

from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User, Message


async def orm_add_user(session: AsyncSession, user_id: int,):
    try:
        # Проверяем, существует ли уже такой пользователь
        result = await session.execute(select(User).filter(User.user_id == user_id))
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            # Если пользователь не существует, вставляем новую запись
            await session.execute(insert(User).values(user_id=user_id))
            await session.commit()
            print(f"Пользователь {user_id} успешно добавлен с 10к токенами.")
        else:
            print(f"Пользователь {user_id} уже существует.")
    except Exception as e:
        # Обработка ошибок и откат транзакции
        await session.rollback()
        print(f"Ошибка: {e}")


async def orm_save_message(session: AsyncSession, user_id: int, role: str, message: str, tokens: int):
    new_message = Message(
        user_id=user_id,
        role=role,
        content=message,
        tokens=tokens
    )
    session.add(new_message)
    await session.commit()


async def orm_delete_message(session: AsyncSession, message_id: int):
    await session.execute(delete(Message).where(Message.id == message_id))
    await session.commit()


async def orm_delete_messages(session: AsyncSession, user_id: int):
    # Проверяем, есть ли сообщения с таким user_id
    result = await session.execute(select(Message).filter(Message.user_id == user_id))
    messages = result.scalars().all()

    if messages:
        # Если сообщения найдены, выполняем удаление
        await session.execute(delete(Message).filter(Message.user_id == user_id))
        await session.commit()
        print(f"Удалено {len(messages)} сообщений.")
    else:
        print("Сообщения с таким user_id не найдены.")


async def orm_get_messages(session: AsyncSession, user_id: int) -> List[Tuple[int, str, str, int]]:
    result = await session.execute(select(Message).where(Message.user_id == user_id))
    messages = result.scalars().all()
    return [(msg.id, msg.role, msg.content, msg.tokens) for msg in messages]
