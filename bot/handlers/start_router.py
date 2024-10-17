import asyncio
import os
from typing import Union

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from tiktoken import encoding_for_model

from bot.config import BASE_DIR
from bot.database.orm_query import *
from bot.utils.buttons import *
from bot.utils.extra import reduce_messages, encoding
from bot.utils.openai_tools import *
from bot.utils.states import States
from bot.utils.texts import *

start_router = Router()


@start_router.message(CommandStart())
async def start_bot(message: types.Message, session: AsyncSession, state: FSMContext):
    try:
        await orm_add_user(session, message.from_user.id)
    except:
        pass
    await orm_delete_messages(session, message.from_user.id)

    await message.answer(
        text=start_text,
        reply_markup=start_buttons,
    )

    await state.set_state(States.INITIAL)


@start_router.callback_query(F.data.startswith("delete_"))
async def bot_delete_message(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    message_id = int(call.data.split('_')[1]) + 1
    print(message_id)
    await call.message.bot.delete_message(call.message.chat.id, message_id)


@start_router.message(States.CHATGPT)
async def get_error_bot(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer("Подожди, пожалуйста. "
                         "Я обрабатываю по одному сообщению за раз, данное сообщение не будет обработано.",
                         reply_markup=await ok_delete_button(message.message_id))
    print(message.message_id)


@start_router.message(F.text.contains("Очистить историю диалога"))
@start_router.message(Command("reset"))
async def reset_dialog_bot(message: types.Message, session: AsyncSession, state: FSMContext):
    await orm_delete_messages(session, message.from_user.id)

    await message.answer("🧹 Очищена история диалога!\n\n"
                         "Чтобы перезапустить бота, напиши /start.")


@start_router.message(F.text)
async def chatgpt_answer_bot(message: types.Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    # proxy_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    # proxies = await load_proxies_from_url(proxy_url)
    # proxies = load_proxies(os.path.join(BASE_DIR, 'utils', 'proxies.txt'))
    # тут может быть проверка на токены
    # tokens = await orm_get_tokens(session, user_id)

    encoding = encoding_for_model("gpt-4o-mini")

    await state.set_state(States.CHATGPT)
    await message.answer(
        text=f"⏳Я обрабатываю ваш запрос.\n"
             f"Пожалуйста, подождите немного . . ."
    )
    wait_mess_id = message.message_id + 1
    print(wait_mess_id)
    await orm_save_message(
        session,
        user_id=user_id,
        role="user",
        message=message.text,
        tokens=len(encoding.encode(message.text))
    )

    messages = await orm_get_messages(session, user_id)

    start, question_tokens = await reduce_messages(messages)
    print(f"TEST ", start, question_tokens)

    answer = await OpenAiTools.get_chatgpt(start, messages)
    print(answer)
    if answer:
        # answer_tokens = len(await asyncio.get_running_loop().run_in_executor(None, encoding.encode, answer))
        await orm_save_message(session, user_id, "assistant", answer, len(encoding.encode(answer)))

        await message.bot.delete_message(chat_id=message.chat.id, message_id=wait_mess_id)
        await message.answer(
            text=answer,
        )
        await state.set_state(States.INITIAL)
    else:
        await orm_delete_message(session, messages[-1][0])
        await message.bot.delete_message(chat_id=message.chat.id, message_id=wait_mess_id)
        await message.answer(text=f"🧐Что-то пошло не так. Ответа нет")
        await state.set_state(States.INITIAL)
