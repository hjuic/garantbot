from aiogram.types import Message, CallbackQuery
from database.db import *
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.kb import *
from configparser import ConfigParser

config = ConfigParser()


class Close(StatesGroup):
    confirm = State()


async def my_deal(c: CallbackQuery):
    await c.message.answer('<b>Выберите тип сделок:</b>', reply_markup=type_deal())


async def my_deal_(c: CallbackQuery):
    u = ''

    if c.data == 'selldeal':
        if Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'active').first() is not None or Orders.query.filter(
                Orders.seller_tid == c.from_user.id).filter(Orders.status == 'dispute').first() is not None:

            u = Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'active').all() + Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'dispute').all()
            await c.message.answer('<b>🤝Ваши сделки:</b>', reply_markup=list_deals(u))
        else:
            await c.message.answer('У вас нет активных сделок..')
    elif c.data == 'buydeal':
        if Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'active').first() is not None or Orders.query.filter(
            Orders.buyer_tid == c.from_user.id).filter(Orders.status == 'dispute').first() is not None:

            u = Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'active').all() + Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'dispute').all()
            await c.message.answer('<b>🤝Ваши сделки:</b>', reply_markup=list_deals(u))
        else:
            await c.message.answer('У вас нет активных сделок..')


async def get_info_deal(c: CallbackQuery):
    try:
        id = c.data.split(':')[1]
        order = Orders.query.filter(Orders.order_id == id).first()
        status = 'Активна' if order.status == 'active' else 'Арбитраж'
        if status == 'Активна':
            if order.buyer_tid == c.from_user.id:
                seller = Users.query.filter(Users.tid == order.seller_tid).first()
                await c.message.bot.send_message(order.buyer_tid, f'''
Сделка <b>№{order.order_id}</b> | <b>Активна</b>

От @{c.from_user.username} для {seller.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
            ''', reply_markup=menu_of_deal_buyer(order.order_id))
            else:
                buyer = Users.query.filter(Users.tid == order.buyer_tid).first()
                await c.message.edit_text(f'''
Сделка <b>№{order.order_id}</b> | <b>Активна</b>

От {buyer.username} для @{c.from_user.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
            ''', reply_markup=menu_of_deal_seller(order.order_id))
        else:
            if order.buyer_tid == c.from_user.id:
                seller = Users.query.filter(Users.tid == order.seller_tid).first()
                await c.message.bot.send_message(order.buyer_tid, f'''
✏ Сделка <b>№{order.order_id}</b> | <b>💢 Арбитраж</b>

🔍 От @{c.from_user.username} для {seller.username}
💸 Сумма: <b>{order.summa} {order.coin}</b>
📃 Условия: {order.ifelse}
                        ''')
            else:
                buyer = Users.query.filter(Users.tid == order.buyer_tid).first()
                await c.message.edit_text(f'''
✏ Сделка <b>№{order.order_id}</b> | <b>💢 Арбитраж</b>

🔍 От {buyer.username} для @{c.from_user.username}
💸 Сумма: <b>{order.summa} {order.coin}</b>
📃 Условия: {order.ifelse}
                        ''')


    except Exception as e:
        print(e)


async def closedeal(c: CallbackQuery, state: FSMContext):
    order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
    await c.message.answer(f'<b>Вы уверены, что хотите завершить сделку №{order.order_id}</b>?',
                           reply_markup=confirmclosee(c.data.split(':')[1]))
    await Close.confirm.set()


async def confirmclose(c: CallbackQuery, state: FSMContext):
    if 'confirmclose' in c.data:
        order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
        if order.status == 'active':
            order.status = 'success'
            session.add(order)
            session.commit()
            await c.message.edit_text('<b>✅ Сделка успешно закрыта, деньги переведены продавцу!</b>',
                                      reply_markup=give_review(c.data.split(':')[1]))
            seller = Users.query.filter(Users.tid == order.seller_tid).first()
            await c.message.bot.send_message(seller.tid,
                                             f'Покупатель закрыл сделку <b>№{order.order_id}</b>. Деньги зачислены на ваш баланс.')
            if order.coin == 'eur':
                seller.balance_eur += order.summa
            elif order.coin == 'rub':
                seller.balance_rub = + order.summa
            session.add(seller)
            session.commit()
            await state.finish()
    else:
        await c.message.edit_text('Действие невозможно')
        await state.finish()


async def arbirt(c: CallbackQuery):
    await c.message.answer(f'Вы уверены, что хотите открыть спор по сделке <b>№{c.data.split(":")[1]}</b>?',
                           reply_markup=confirm_arbitr(c.data.split(':')[1]))


async def confirm_arbitra(c: CallbackQuery):
    order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
    if order.status == 'active':
        order.status = 'dispute'
        session.add(order)
        session.commit()
        config.read('config/config.ini')
        await c.message.bot.send_message(order.seller_tid,
                                         f'Сделка <b>№{c.data.split(":")[1]}</b> переведена в арбитраж! Ожидайте сообщения администратора')
        await c.message.bot.send_message(order.buyer_tid,
                                         f'Сделка <b>№{c.data.split(":")[1]}</b> переведена в арбитраж! Ожидайте сообщения администратора')
        seller = Users.query.filter(Users.tid == order.seller_tid).first()
        buyer = Users.query.filter(Users.tid == order.buyer_tid).first()
        await c.message.bot.send_message(config['chats']['admin'], f'''
Сделка <b>№{c.data.split(":")[1]}</b> переведена в арбитраж!

Покупатель: {buyer.username} | ID: <code>{buyer.tid}</code>
Продавец: {seller.username} | ID: <code>{seller.tid}</code>
Сумма: <b>{order.summa} {order.coin}</b>

Условия: {order.ifelse}
''', reply_markup=dispute_admin(buyer.tid, seller.tid, order.order_id))
    else:
        await c.message.answer('Действие невозможно')


async def cancel_arbitr(c: CallbackQuery):
    await c.message.edit_text('Действие отменено')


async def cancel_deal(c: CallbackQuery):
    await c.message.answer(f'Вы действительно хотите отменить сделку<b> №{c.data.split(":")[1]}</b>?',
                           reply_markup=confirmcanceldeal(c.data.split(':')[1]))


async def confirmcancel(c: CallbackQuery):
    order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
    if order.status == 'active':

        order.status = 'canceled'
        session.add(order)
        session.commit()
        buyer = Users.query.filter(Users.tid == order.buyer_tid).first()
        if order.coin == 'eur':
            buyer.balance_eur += order.summa
        elif order.coin == 'rub':
            buyer.balance_rub += order.summa
        session.add(buyer)
        session.commit()

        await c.message.bot.send_message(order.buyer_tid,
                                         f'❌ Сделка <b>№{order.order_id}</b> была отменена продавцом. Деньги вернулись на баланс покупателю.')

        await c.message.bot.send_message(order.seller_tid,
                                         f'❌ Сделка <b>№{order.order_id}</b> была отменена продавцом. Деньги вернулись на баланс покупателю.')
    else:
        await c.message.answer('Действие невозможно')


def reg_my_deal(dp: Dispatcher):
    dp.register_callback_query_handler(my_deal, text='activedeals', state='*', is_not_banned=True)
    dp.register_callback_query_handler(my_deal_, text='selldeal', state='*', is_not_banned=True)
    dp.register_callback_query_handler(my_deal_, text='buydeal', state='*', is_not_banned=True)
    dp.register_callback_query_handler(get_info_deal, text_contains='mydeal:', is_not_banned=True)
    dp.register_callback_query_handler(closedeal, text_contains='closedeal:', state='*', is_not_banned=True)
    dp.register_callback_query_handler(confirmclose, text_contains='confirmclose:', state=Close.confirm,
                                       is_not_banned=True)
    dp.register_callback_query_handler(confirmclose, text_contains='cancelclose:', state=Close.confirm,
                                       is_not_banned=True)
    dp.register_callback_query_handler(arbirt, text_contains='arbitr:', is_not_banned=True)
    dp.register_callback_query_handler(confirm_arbitra, text_contains='arbitr_confirm:', is_not_banned=True)
    dp.register_callback_query_handler(cancel_arbitr, text_contains='arbitr_cancel:', is_not_banned=True)
    dp.register_callback_query_handler(cancel_deal, text_contains='canceldeal:', is_not_banned=True)
    dp.register_callback_query_handler(confirmcancel, text_contains='confirmcancelldeal:', is_not_banned=True)
    dp.register_callback_query_handler(cancel_arbitr, text_contains='cancelcancelldeal:', is_not_banned=True)
