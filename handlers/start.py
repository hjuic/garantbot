from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher
from keyboards.kb import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from database.db import *


class Reglament(StatesGroup):
    accepting = State()


async def start(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        await state.finish()
    if Users.query.filter(Users.tid == message.from_user.id).first() is not None:
        await message.answer('''<b>⌚ Меню</b>''', reply_markup=menu())

    else:
        await message.answer(
            '<b>♻ Перед тем, как начать пользоваться ботом, необходимо подтведить, что вы <a '
            'href="https://telegra.ph/PravilaSoglashenie-Bosss-garanta-12-29">ознакомлены с правилами.</a></b>',
            reply_markup=accept())
        await Reglament.accepting.set()


async def accepting_rules(c: CallbackQuery, state: FSMContext):
    try:
        user = Users(
            tid=c.from_user.id,
            username='@' + c.from_user.username
        )
        session.add(user)
        session.commit()
        await c.message.edit_text('<b>✅ Успешно! Чтобы начать пользоваться ботом напишите -> /start</b>')
        await state.finish()
    except Exception as e:
        print(e)


def register_start(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*', )
    dp.register_callback_query_handler(accepting_rules, text='accept', state=Reglament.accepting)
