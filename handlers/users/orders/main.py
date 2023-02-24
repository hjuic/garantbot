from aiogram.types import Message, CallbackQuery
from database.db import *
from keyboards.kb import *
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from configparser import ConfigParser
import random

config = ConfigParser()


class FindUser(StatesGroup):
    user = State()


class NewOrder(StatesGroup):
    seller = State()
    sum = State()
    coin = State()
    ifelse = State()
    confirm = State()


async def mainmenu(message: Message):
    await message.answer_photo(
        photo='https://old.keysystems.ru/upload/iblock/50b/50bdea8172e33faba1850629d035b97e.jpg',
        caption='<b>Меню сделок:</b>', reply_markup=menu_orders())


async def new_order(message: Message, state: FSMContext):
    await message.answer('<b>🤖 Введите @username продавца</b>')
    await FindUser.user.set()


async def finduser(message: Message, state: FSMContext):
    msg = message.text
    if msg[0] == '@':
        try:
            seller = Users.query.filter(Users.username == message.text).first()
            await message.answer(f'''
<b>👑 Пользователь {message.text} | 🆔 : <code>{seller.tid}</code>

⚖ Всего продаж: {len(Orders.query.filter(Orders.seller_tid == seller.tid).filter(Orders.status == 'success').all())}
    На сумму (RUB): {sum(i.summa for i in Orders.query.filter(Orders.seller_tid == seller.tid).filter(Orders.coin == 'rub').filter(Orders.status == 'success').all())}
    На сумму (EUR): {sum(i.summa for i in Orders.query.filter(Orders.seller_tid == seller.tid).filter(Orders.coin == 'eur').filter(Orders.status == 'success').all())} 
⚖ Всего покупок: {len(Orders.query.filter(Orders.buyer_tid == seller.tid).filter(Orders.status == 'success').all())}
    На сумму (RUB): {sum(i.summa for i in Orders.query.filter(Orders.buyer_tid == seller.tid).filter(Orders.coin == 'rub').filter(Orders.status == 'success').all())}
    На сумму (EUR): {sum(i.summa for i in Orders.query.filter(Orders.buyer_tid == seller.tid).filter(Orders.coin == 'eur').filter(Orders.status == 'success').all())}</b>
            ''', reply_markup=seller_kb(seller.tid))
            await state.finish()
        except Exception as e:
            print(e)
            await message.answer('Пользователь не найден!')
            await state.finish()
    else:
        await message.answer('Неверный формат!')
        await state.finish()


async def view_review(c: CallbackQuery):
    try:
        id = c.data.split(':')[1]
        user = Users.query.filter(Users.tid == id).first()
        text = f'Отзывы {user.username}:\n'
        if Reviews.query.filter(Reviews.seller_tid == id).first() is not None:

            u = Reviews.query.filter(Reviews.seller_tid == id).all()
            for i in u:
                buyer = await c.bot.get_chat(i.buyer_tid)
                text += f'''
<b>От @{buyer['username']}:
<code>{i.text}</code></b>\n'''

            await c.message.answer(text)
        else:
            await c.message.answer('У пользователя еще нет отзывов...')
    except Exception as e:
        print(e)


async def request_deal(c: CallbackQuery, state: FSMContext):
    await NewOrder.seller.set()
    await state.update_data(seller=c.data.split(':')[1])
    await c.message.answer('<b>💻 Введите сумму и валюту (<i>rub, eur</i>) через запятую\nПример: <i>5000,eur</i></b>')
    await NewOrder.sum.set()


async def set_sum(message: Message, state: FSMContext):
    sum = message.text.split(',')[0]
    coin = message.text.split(',')[1]

    if sum.isdigit():
        if coin == 'eur' or coin == 'rub':
            await state.update_data(coin=coin)
            await state.update_data(sum=sum)
            await message.answer('''<b>✏️Введите условия сделки:</b>

<i>Очень важно ввести условия сделки максимально точно, так-как малейшая неуказанная деталь может повлиять на решение спора❗</i>''')
            await NewOrder.ifelse.set()
        else:
            await message.answer('Неверный формат! -> /start')
            await state.finish()
    else:
        await message.answer('Неверный формат! Действие отменено.')
        await state.finish()


async def set_ifelse(message: Message, state: FSMContext):
    await state.update_data(ifelse=message.text)
    data = await state.get_data()
    seller = await message.bot.get_chat(data['seller'])
    await message.answer(f'''
<b>❗ Подтвердите запрос на сделку:</b>

🔍 Для: <b>@{seller['username']}</b>
💸 Сумма: <b>{data['sum']} {data['coin']}</b>
📄 Условия: {message.text}
    ''', reply_markup=confirm_request())
    await NewOrder.confirm.set()


async def confirmrequest(c: CallbackQuery, state: FSMContext):
    if c.data == 'startdeal':
        data = await state.get_data()
        user = Users.query.filter(Users.tid == c.from_user.id).first()
        if data['coin'] == 'eur' and user.balance_eur >= float(data['sum']) or data[
            'coin'] == 'rub' and user.balance_rub >= float(data['sum']):
            orderid = random.randint(1111, 9999999)
            order = Orders(
                order_id=orderid,
                buyer_tid=c.from_user.id,
                seller_tid=int(data['seller']),
                summa=float(data['sum']),
                coin=data['coin'],
                ifelse=data['ifelse']
            )
            session.add(order)
            session.commit()
            await c.message.bot.send_message(data['seller'], f'''
<b>❗ Запрос на сделку от @{c.from_user.username}</b>

💸 Сумма: <b>{data['sum']} {data['coin']}</b>
📄 Условия: {data['ifelse']}
            ''', reply_markup=accept_request(orderid))

            if data['coin'] == 'eur':
                user.balance_eur = user.balance_eur - float(data['sum'])
            elif data['coin'] == 'rub':
                user.balance_rub = user.balance_rub - float(data['sum'])
            session.add(user)
            session.commit()
            await c.message.edit_text('Запрос на сделку отправлен!')
            await state.finish()
        else:
            await c.message.answer('<b>Недостаточно средств для сделки! Пополните баланс и попробуйте еще раз</b>')

    else:
        await c.message.edit_text('Действие отменено')
        await state.finish()


async def accept_or_not_deal(c: CallbackQuery):
    if 'acceptdeal' in c.data:
        order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
        order.status = 'active'
        session.add(order)
        session.commit()
        buyer = await c.message.bot.get_chat(order.buyer_tid)
        await c.message.edit_text(f'''
✏ Сделка <b>№{order.order_id}</b> | <b>♻ Активна</b>

🔍 От @{buyer['username']} для @{c.from_user.username}
💸 Сумма: <b>{order.summa} {order.coin}</b>
📄 Условия: {order.ifelse}
        ''', reply_markup=menu_of_deal_seller(order.order_id))
        await c.message.bot.send_message(order.buyer_tid, f'''
✏ Сделка <b>№{order.order_id}</b> | <b>♻Активна</b>

🔍 От @{buyer['username']} для @{c.from_user.username}
💸 Сумма: <b>{order.summa} {order.coin}</b>
📄 Условия: {order.ifelse}
        ''', reply_markup=menu_of_deal_buyer(order.order_id))
    else:
        order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
        order.status = 'canceled'
        session.add(order)
        session.commit()
        user = Users.query.filter(Users.tid == order.buyer_tid).first()
        if order.coin == 'eur':
            user.balance_eur += order.summa
        elif order.coin == 'rub':
            user.balance_rub += order.summa
        session.add(user)
        session.commit()
        await c.message.edit_text('<b>Запрос отклонен!</b>')
        await c.message.bot.send_message(user.tid, f'<b>Продавец @{c.from_user.username} отклонил запрос на сделку</b>')


def register_main_deal(dp: Dispatcher):
    dp.register_callback_query_handler(view_review, state='*', is_not_banned=True, text_contains='showreviews:')
    dp.register_message_handler(mainmenu, text='♻ Мои сделки', state='*', is_not_banned=True)
    dp.register_message_handler(new_order, text='➕ Новая сделка', is_not_banned=True)
    dp.register_message_handler(finduser, state=FindUser.user, is_not_banned=True)
    dp.register_callback_query_handler(request_deal, state='*', text_contains='requestdeal:', is_not_banned=True)
    dp.register_message_handler(set_sum, state=NewOrder.sum, is_not_banned=True)
    dp.register_message_handler(set_ifelse, state=NewOrder.ifelse, is_not_banned=True)
    dp.register_callback_query_handler(confirmrequest, state=NewOrder.confirm, is_not_banned=True)
    dp.register_callback_query_handler(accept_or_not_deal, state='*', text_contains='acceptdeal:', is_not_banned=True)
    dp.register_callback_query_handler(accept_or_not_deal, state='*', text_contains='declinedeal:', is_not_banned=True)
