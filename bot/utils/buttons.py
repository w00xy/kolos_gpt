from bot.utils.kbds.inline import *
from bot.utils.kbds.keyboards import get_kb

start_buttons = get_kb(
                "🧹Очистить историю диалога",
                sizes=(1,)
)


async def ok_delete_button(message_id):
    return get_inlineMix_btns(
        btns={
            "Понятно": f"delete_{message_id}"
        }
    )

