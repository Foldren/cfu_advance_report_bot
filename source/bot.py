import logging
from asyncio import run
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from redis.asyncio import from_url
from tortoise import run_async
from components import handlers
from components.dialogs import menu, create_advance_report, failure_advance_report, upload_advance_report
from components.filters import IsParticipantFilter
from config import TOKEN, REDIS_URL
from init_db import init_db


dialogs = [
    menu, create_advance_report, failure_advance_report, upload_advance_report
]


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

    storage = RedisStorage(
        redis=await from_url(REDIS_URL, db=15, decode_responses=True),
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )  # В 15 db стейты

    dp = Dispatcher(storage=storage)

    dp.callback_query.filter(IsParticipantFilter())
    dp.message.filter(IsParticipantFilter())

    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    dp.include_routers(handlers.router, *dialogs)
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    run_async(init_db())
    run(main())

