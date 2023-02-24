from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher
from keyboards.kb import *
from database.db import Users


async def menu_admin(message: Message):
    await message.answer(f'Админ-панель\nКоличество пользователей: {len(Users.query.filter().all())}',
                         reply_markup=admin_menu())


def register_admin_menu(dp: Dispatcher):
    dp.register_message_handler(menu_admin, commands=['admin'], is_admin=True)
