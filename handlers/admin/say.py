from aiogram.types import Message, CallbackQuery
from database.db import *
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class Say(StatesGroup):
    content = State()


async def go_to(c: CallbackQuery, state: FSMContext):
    await c.message.answer('<b>Отправьте контент рассылки:</b>')
    await Say.content.set()


async def say_photo(message: Message, state: FSMContext):
    await message.answer('Рассылка запущена!')
    await state.finish()
    for i in Users.query.filter(Users.status != 'banned').all():
        try:
            await message.bot.send_photo(i.tid, photo=message.photo[-1].file_id, caption=message.caption)
        except Exception as e:
            print(e)
            pass
    await message.answer('Рассылка завершена!')


async def say(message: Message, state: FSMContext):
    await message.answer('Рассылка запущена!')
    await state.finish()
    for i in Users.query.filter(Users.status != 'banned').all():

        try:
            await message.bot.send_message(i.tid, text=message.text)
        except Exception as e:
            print(e)
            pass
    await message.answer('Рассылка завершена!')


def reg_say_admin(dp: Dispatcher):
    dp.register_callback_query_handler(go_to, state='*', text='say', is_admin=True)
    dp.register_message_handler(say_photo, content_types=['photo'], state=Say.content, is_admin=True)
    dp.register_message_handler(say, state=Say.content, is_admin=True)
