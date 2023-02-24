from aiogram.types import CallbackQuery
from database.db import *
from keyboards.kb import *
from aiogram import Dispatcher


async def choose_s_deal(c: CallbackQuery):
    await c.message.answer('<b>Выберите тип сделок:</b>', reply_markup=chose_s())


async def get_deal(c: CallbackQuery):
    u = ''
    if c.data == 's_sell_deal':
        if Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'success').first() is not None or Orders.query.filter(
                Orders.seller_tid == c.from_user.id).filter(Orders.status == 'sucessdispute').first() is not None:
            u = Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'success').all() + Orders.query.filter(Orders.seller_tid == c.from_user.id).filter(
                Orders.status == 'sucessdispute').all()
            await c.message.answer('<b>🤝Ваши сделки:</b>', reply_markup=list_deals_s(u))
        else:
            await c.message.answer('У вас нет завершенных сделок..')
    if c.data == 's_buy_deal':
        if Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'success').first() is not None or Orders.query.filter(
                Orders.buyer_tid == c.from_user.id).filter(Orders.status == 'sucessdispute').first() is not None:

            u = Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'success').all() + Orders.query.filter(Orders.buyer_tid == c.from_user.id).filter(
                Orders.status == 'sucessdispute').all()
            await c.message.answer('<b>🤝Ваши сделки:</b>', reply_markup=list_deals_s(u))
        else:
            await c.message.answer('У вас нет завершенных сделок..')


async def show_success_deal(c: CallbackQuery):
    order = Orders.query.filter(Orders.order_id == c.data.split(':')[1]).first()
    if order.buyer_tid == c.from_user.id:
        seller = Users.query.filter(Users.tid == order.seller_tid).first()
        await c.message.bot.send_message(order.buyer_tid, f'''
    Сделка <b>№{order.order_id}</b> | <b>Завершена</b>

    От @{c.from_user.username} для {seller.username}
    Сумма: <b>{order.summa} {order.coin}</b>
    Условия: {order.ifelse}
                ''')
    else:
        buyer = Users.query.filter(Users.tid == order.buyer_tid).first()
        await c.message.edit_text(f'''
Сделка <b>№{order.order_id}</b> | <b>Завершена</b>

От {buyer.username} для @{c.from_user.username}
Сумма: <b>{order.summa} {order.coin}</b>
Условия: {order.ifelse}
                ''')


def reg_success(dp: Dispatcher):
    dp.register_callback_query_handler(choose_s_deal, text='success_orders', is_not_banned=True)
    dp.register_callback_query_handler(get_deal, text='s_sell_deal', is_not_banned=True)
    dp.register_callback_query_handler(get_deal, text='s_buy_deal', is_not_banned=True)
    dp.register_callback_query_handler(show_success_deal, text_contains='mydealss:', is_not_banned=True)
