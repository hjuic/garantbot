from aiogram.types import Message, CallbackQuery
from database.db import *
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.kb import *


class ChangeBalance(StatesGroup):
    userr = State()
    content = State()


class FindUserAdm(StatesGroup):
    user = State()


async def finduser(c: CallbackQuery, state: FSMContext):
    await c.message.answer('Введите id или @username пользователя:')
    await FindUserAdm.user.set()


async def pre_balance(c: CallbackQuery, state: FSMContext):
    await ChangeBalance.userr.set()
    await state.update_data(userr=c.data.split(':')[1])
    await c.message.answer('Введите сколько добавить на баланс пользователю\nПример:<i>500 eur</i>')
    await ChangeBalance.content.set()


async def userpanel(message: Message, state: FSMContext):
    if message.text.isdigit():
        try:
            id = message.text
            user = Users.query.filter(Users.tid == id).first()
            await message.answer(f'''
    Пользователь {user.username} | ID: <code>{user.tid}</code>

    💴 Баланс RUB: <b>{user.balance_rub}</b>
    💶 Баланс EUR: <b>{user.balance_eur}</b>

    📚 Всего сделок: <b>{len(Orders.query.filter(Orders.seller_tid == id).filter(Orders.status == 'success').all())}</b>
    💡 Рейтинг: <b>{user.rating}/10</b>
            ''', reply_markup=panel_of_user(user.tid))
        except Exception as e:
            print(e)
            await message.answer('Пользователь не найден!')
    elif '@' in message.text:
        try:
            username = message.text
            user = Users.query.filter(Users.username == username).first()
            await message.answer(f'''
            Пользователь {user.username} | ID: <code>{user.tid}</code>

💴 Баланс RUB: <b>{user.balance_rub}</b>
💶 Баланс EUR: <b>{user.balance_eur}</b>

📚 Всего сделок: <b>{len(Orders.query.filter(Orders.seller_tid == user.tid).filter(Orders.status == 'success').all())}</b> 💡 Рейтинг: <b>{user.rating}/10</b> 
                    ''', reply_markup=panel_of_user(user.tid))
        except Exception as e:
            print(e)
            await message.answer('Пользователь не найден!')
    await state.finish()


async def addbalance(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        id = data['userr']
        sum = message.text.split(' ')[0]
        coin = message.text.split(' ')[1]
        user = Users.query.filter(Users.tid == id).first()
        if coin == 'rub':
            user.balance_rub += float(sum)
        elif coin == 'eur':
            user.balance_eur += float(sum)
        session.add(user)
        session.commit()
        await message.answer('Баланс изменен!')
        await message.bot.send_message(user.tid, f'На ваш баланс зачислено <b>{sum}{coin}</b>✅')
    except Exception as e:
        print(e)
        await message.answer('Юзер не найден')
        session.rollback()
    await state.finish()


async def ban_user(c: CallbackQuery):
    try:
        id = c.data.split(':')[1]
        user = Users.query.filter(Users.tid == id).first()
        user.status = 'banned'
        session.add(user)
        session.commit()
        await c.message.answer('Пользователь заблокирован!')

    except:
        await c.message.answer('Пользователь не найден')
        session.rollback()


async def unban_user(c: CallbackQuery):
    try:
        id = c.data.split(':')[1]
        user = Users.query.filter(Users.tid == id).first()
        if user.status == 'banned':
            user.status = 'user'
            session.add(user)
            session.commit()
            await c.message.answer('Пользователь разблокирован!')
        else:
            await c.message.answer('Пользователь не заблокирован')
    except:
        await c.message.answer('Пользователь не найден')
        session.rollback()


def reg_user_admin(dp: Dispatcher):
    dp.register_callback_query_handler(finduser, text='findadmin', is_admin=True)
    dp.register_callback_query_handler(pre_balance, text_contains='addbalance:')
    dp.register_message_handler(userpanel, state=FindUserAdm.user, is_admin=True)
    dp.register_message_handler(addbalance, state=ChangeBalance.content, is_admin=True)
    dp.register_callback_query_handler(ban_user, text_contains='banuser:', is_admin=True)
    dp.register_callback_query_handler(unban_user, text_contains='unban:', is_admin=True)
