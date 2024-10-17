from tiktoken import encoding_for_model
from typing_extensions import List, Tuple

from bot.database.engine import session_maker
from bot.database.orm_query import orm_delete_message

encoding = encoding_for_model("gpt-4o-mini")


async def reduce_messages(messages: List[Tuple[int, str, str, int]]) -> Tuple[int, int]:
    question_tokens = 0
    i = len(messages) - 1
    while i >= 0:
        if question_tokens + messages[i][3] < 128000:
            question_tokens += messages[i][3]
        else:
            break
        i -= 1
    for j in range(i+1):
        async with session_maker() as session:
            await orm_delete_message(session, messages[i][0])
    return i+1, question_tokens
