from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from database.db import Users


class IsAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        user = Users.query.filter(Users.tid == message.from_user.id).first()
        if user.status != 'admin':
            await message.answer('Вы не админ')
            return False
        else:
            return True
