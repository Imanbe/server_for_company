import asyncio

from src.BD.users_db import init_db, add_user
from ..Configs.config import settings


async def initialize_bd():
    await init_db()
    for _key, _val in settings.USERS.items():
        await add_user(_key, _val.get('user_name'))

if __name__ == '__main__':
    asyncio.run(initialize_bd())
