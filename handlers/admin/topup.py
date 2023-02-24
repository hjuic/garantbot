from aiogram.types import CallbackQuery
from aiogram import Dispatcher
from database.db import *


async def iban_success(c: CallbackQuery):
    user = Users.query.filter(Users.tid == c.data.split(':')[3]).first()
    order = TopUps.query.filter(TopUps.topup_id == c.data.split(':')[1]).first()
    order.status = 'success'
    session.add(order)
    session.commit()
    user.balance_eur = user.balance_eur + float(c.data.split(':')[2])
    session.add(user)
    session.commit()

    await c.message.bot.send_message(user.tid,
                                     f'<b>Ваш платеж на IBAN был найден! Вам зачислили {c.data.split(":")[2]} евро на баланс✅</b>')
    await c.message.answer('Платеж зачислен!')


async def iban_cancel(c: CallbackQuery):
    order = TopUps.query.filter(TopUps.topup_id == c.data.split(':')[1]).first()
    order.status = 'cancel'
    session.add(order)
    session.commit()

    await c.message.bot.send_message(c.data.split(':')[3],
                                     '<b>Ваша оплата на IBAN не найдена! Деньги не зачислены.❌</b>')


async def wd_accept(c: CallbackQuery):
    # user = Users.query.filter(Users.tid == c.data.split(':')[1]).first()
    await c.bot.send_message(c.data.split(':')[1],
                             '<b>👍 Ваша заявка на вывод была одобрена!</b> Ожидайте поступления денег на счет.')
    await c.message.answer('Сообщение юзеру было отправлено!')


async def cancel_wd(c: CallbackQuery):
    await c.bot.send_message(c.data.split(':')[1], '''<b>К сожалению, ваша заявка на вывод средств была отменена😢</b>
    <i>Свяжитесь с нашей командой для решения этой проблемы⛑</i>''')
    await c.message.answer('Сообщение юзеру было отправлено!')


async def dispute_res(c: CallbackQuery):
    try:
        if c.data.split(':')[0] == 'seller':
            seller = c.data.split(':')[1]
            buyer = c.data.split(':')[2]
            order = Orders.query.filter(Orders.order_id == c.data.split(':')[3]).first()
            seller_db = Users.query.filter(Users.tid == seller).first()
            buyer_db = Users.query.filter(Users.tid == buyer).first()
            if order.coin == 'eur':
                seller_db.balance_eur += order.summa
            elif order.coin == 'rub':
                seller_db.balance_rub += order.summa
            session.add(seller_db)
            session.commit()
            await c.message.bot.send_message(seller, f'''
Сделка <b>№{order.order_id}</b> | <b>🤴 Вы выиграли арбитраж</b>

От {buyer_db.username} для {seller_db.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
            ''')
            await c.message.bot.send_message(buyer, f'''
Сделка <b>№{order.order_id}</b> | <b>👨‍⚖ Вы проиграли арбитраж</b>

От {buyer_db.username} для {seller_db.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
                        ''')
            await c.message.answer('Арбитраж закрыт в сторону продавца!')
        else:
            buyer = c.data.split(':')[1]
            seller = c.data.split(':')[2]
            order = Orders.query.filter(Orders.order_id == c.data.split(':')[3]).first()
            seller_db = Users.query.filter(Users.tid == seller).first()
            buyer_db = Users.query.filter(Users.tid == buyer).first()
            if order.coin == 'eur':
                buyer_db.balance_eur += order.summa
            elif order.coin == 'rub':
                buyer_db.balance_rub += order.summa
            session.add(buyer_db)
            session.commit()
            await c.message.bot.send_message(buyer, f'''
Сделка <b>№{order.order_id}</b> | <b>🤴 Вы выиграли арбитраж</b>

От {buyer_db.username} для {seller_db.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
                        ''')
            await c.message.bot.send_message(seller, f'''
Сделка <b>№{order.order_id}</b> | <b>👨‍⚖ Вы проиграли арбитраж</b>

От {buyer_db.username} для {seller_db.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
                                    ''')
            await c.message.answer('Арбитраж закрыт в сторону покупателя!')
        order.status = 'sucessdispute'
        session.add(order)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


def register_admin_topup(dp: Dispatcher):
    dp.register_callback_query_handler(dispute_res, is_admin=True, text_contains='seller:')
    dp.register_callback_query_handler(dispute_res, is_admin=True, text_contains='buyer:')
    dp.register_callback_query_handler(wd_accept, is_admin=True, text_contains='okwithd:')
    dp.register_callback_query_handler(cancel_wd, is_admin=True, text_contains='nowithd:')
    dp.register_callback_query_handler(iban_success, is_admin=True, text_contains='ibansuccess:')
    dp.register_callback_query_handler(iban_cancel, is_admin=True, text_contains='ibancancell:')
