from aiogram import Bot, Dispatcher, Router
from dotenv import find_dotenv, load_dotenv
import asyncio
import os

from bd import sql
from hendlers.users import router_user

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN_API'))
dp = Dispatcher()

router = Router()
dp.include_routers(router_user)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await sql.init_db()
    await sql.create_user()
    print("⚔️🛡️🏹🗡️⚔️🛡️🏹🗡️⚔️🛡️🏹🗡️")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())