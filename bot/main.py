import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats

from bot.config import BOT_TOKEN
from bot.database.engine import session_maker, create_db, drop_db
from bot.handlers.handlers import routers
from bot.middlewares.db import DataBaseSession
from bot.utils.bot_commands import command_list


# creating database
async def on_startup():

    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown():
    print('Бот упал')


async def main():
    # bot setting
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    dp = Dispatcher()

    # on_start_up and shotdown functions
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


    # drop offline messages
    await bot.delete_webhook(drop_pending_updates=True)

    # подключение роутеров
    for router in routers:
        dp.include_router(router)

    # connecting the middlewares
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # кнопки из меню справа снизу
    await bot.set_my_commands(commands=command_list, scope=BotCommandScopeAllPrivateChats())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
