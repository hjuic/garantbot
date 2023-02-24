from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from database.db import Users


class IsNotBanned(BoundFilter):
    key = 'is_not_banned'

    def __init__(self, is_not_banned):
        self.is_not_banned = is_not_banned

    async def check(self, message: types.Message):
        user = Users.query.filter(Users.tid == message.from_user.id).first()
        if user.status == 'banned':
            await message.answer('Вы были заблокированы в боте')
            return False

        else:
            #await message.answer('Вы были заблокированы в боте')
            return True
