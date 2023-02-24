from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from database.db import *


class NewReview(StatesGroup):
    order_id = State()
    text = State()
    rating = State()


async def give_review_now(c: CallbackQuery, state: FSMContext):
    await NewReview.order_id.set()
    await state.update_data(order_id=c.data.split(':')[1])
    await c.message.answer('<b>Введите текст отзыва:</b>')
    await NewReview.text.set()


async def set_text(message: Message, state: FSMContext):
    await message.answer('<b>Введите число до 10, как оценку проделанной работы:</b>')
    await state.update_data(text=message.text)
    await NewReview.rating.set()


async def set_rating(message: Message, state: FSMContext):
    try:
        if message.text.isdigit() and float(message.text) <= 10:
            await state.update_data(rating=message.text)
            data = await state.get_data()
            order = Orders.query.filter(Orders.order_id == data['order_id']).first()
            review = Reviews(
                buyer_tid=order.buyer_tid,
                seller_tid=order.seller_tid,
                text=data['text'],
                rating=float(message.text),
                order_id=data['order_id']
            )
            session.add(review)
            session.commit()
            await state.finish()
            seller = Users.query.filter(Users.tid == order.seller_tid).first()
            seller.rating = sum(i.rating for i in Reviews.query.filter(Reviews.seller_tid == seller.tid).all()) / len(
                Reviews.query.filter(Reviews.seller_tid == seller.tid).all())
            session.add(seller)
            session.commit()
            await message.answer('<b>Отзыв оставлен!</b>')

        else:
            await message.answer('Неверный формат!')
            await state.finish()
    except:
        await message.answer('Действие невозможно')


def reg_review(dp: Dispatcher):
    dp.register_callback_query_handler(give_review_now, text_contains='givereview', is_not_banned=True)
    dp.register_message_handler(set_text, state=NewReview.text, is_not_banned=True)
    dp.register_message_handler(set_rating, state=NewReview.rating, is_not_banned=True)
