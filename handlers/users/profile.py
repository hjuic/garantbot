import random

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from api.crypto import *
from database.db import *
from keyboards.kb import *

config = ConfigParser()


class WD(StatesGroup):
    method = State()
    req = State()


class TopUp(StatesGroup):
    method = State()
    currency = State()
    sum = State()


async def my_profile(message: Message, state: FSMContext):
    user = Users.query.filter(Users.tid == message.from_user.id).first()
    if user is not None:
        if await state.get_state() is not None:
            await state.finish()

        await message.answer_photo(
            photo='https://aleksnovikov.ru/wp-content/uploads/2018/03/Telegram-dlya-biznesa.jpg', caption=f'''
<b>👶 Твой профиль | ID: <code>{message.from_user.id}</code>

💴 Баланс RUB: {user.balance_rub}
💶 Баланс EUR: {user.balance_eur}

📚 Всего сделок: {len(Orders.query.filter(Orders.seller_tid == message.from_user.id).filter(Orders.status == 'success').all())} 
💡 Рейтинг: {user.rating}/10</b>''', reply_markup=profile())


async def my_reviews(c: CallbackQuery):
    text = f'Отзывы @{c.from_user.username}:\n'
    if Reviews.query.filter(Reviews.seller_tid == c.from_user.id).first() is not None:

        u = Reviews.query.filter(Reviews.seller_tid == c.from_user.id).all()
        for i in u:
            buyer = await c.bot.get_chat(i.buyer_tid)
            text += f'''
<b>От @{buyer['username']}:
<code>  {i.text}</code></b>\n'''

        await c.message.answer(text)
    else:
        await c.message.answer('У вас еще нет отзывов...')


async def withdrawl(c: CallbackQuery):
    await c.message.answer('<b>Выберите платежную систему:</b>', reply_markup=withdraw_kb())


async def go_req(c: CallbackQuery, state: FSMContext):
    await WD.method.set()
    method = ''
    if 'qiwi' in c.data:
        method = 'QIWI'
    elif 'cryptobot' in c.data:
        method = 'CryptoBot'
    else:
        method = 'IBAN'
    await state.update_data(method=method)
    if method == 'QIWI':
        await c.message.answer('<b>Введите номер телефона и сумму через запятую\nПример: </b><i>+79998887766,500</i>')
    elif method == 'CryptoBot':
        await c.message.answer('<b>Введите сумму вывода:</b>')
    elif method == 'IBAN':
        await c.message.answer(
            '<b>Введите имя фамилию, номер счета и сумму через запятую\nПример: </b><i>Denis Alabaev,'
            'AT483200000012345864,5000</i>')
    await WD.req.set()


async def set_rq(message: Message, state: FSMContext):
    await state.update_data(req=message.text)
    data = await state.get_data()
    user = Users.query.filter(Users.tid == message.from_user.id).first()
    if ',' in data['req']:
        if data['method'] == 'qiwi' and float(data['req'].split(',')[1]) <= user.balance_rub or float(
                data['req'].split(',')[2]) <= user.balance_eur and data['method'] == 'IBAN':
            await message.answer('<b>Заявка на вывод успешно отправлена! Ожидайте ответа от администрации</b>')
            await state.finish()

            config.read('config/config.ini')
            await message.bot.send_message(config['chats']['admin'], f'''
    🚨 Новая заявка на вывод!
        От пользователя: @{message.from_user.username} | ID: <code>{message.from_user.id}</code>
        Метод: {data['method']}
        Реквизиты,сумма: {data['req']}
            ''', reply_markup=admin_wd(message.from_user.id))
            if data['method'] == 'QIWI':
                user.balance_rub = user.balance_rub - float(data['req'].split(',')[1])
                session.add(user)
                session.commit()
            else:
                user.balance_eur = user.balance_eur - float(data['req'].split(',')[2])
                session.add(user)
                session.commit()

        else:
            await state.finish()
            await message.answer('Недостаточно средств!')
    else:
        if data['req'].isdigit():
            if float(data['req']) <= user.balance_rub:
                await message.answer('<b>Заявка на вывод успешно отправлена! Ожидайте ответа от администрации</b>')
                await state.finish()

                config.read('config/config.ini')
                user.balance_rub = user.balance_rub - float(data['req'])
                session.add(user)
                session.commit()
                await message.bot.send_message(config['chats']['admin'], f'''
                    🚨 Новая заявка на вывод!
                        От пользователя: @{message.from_user.username} | ID: <code>{message.from_user.id}</code>
                        Метод: {data['method']}
                        Cумма: {data['req']}
                            ''', reply_markup=admin_wd(message.from_user.id))

            else:
                await state.finish()
                await message.answer('Недостаточно средств!')
        else:
            print('a')


async def top_up(c: CallbackQuery, state: FSMContext):
    await c.message.answer('<b>Выберите способ пополнения:</b>', reply_markup=top_up_method())


async def get_method(c: CallbackQuery, state: FSMContext):
    await TopUp.method.set()
    await state.update_data(method=c.data.split(':')[1])
    if c.data.split(':')[1] == 'cryptobot':
        await c.message.answer('<b>Выберите криптовалюту:</b>', reply_markup=set_crypto_())
        await TopUp.currency.set()
    elif c.data.split(':')[1] == 'iban':
        await state.update_data(currency='eur')
        await c.message.answer('<b>💶 Введите сумму в EURO:</b>')
        await TopUp.sum.set()
    else:
        await state.update_data(currency='rub')
        await c.message.answer('<b>💴Введите сумму в RUB:</b>')
        await TopUp.sum.set()


async def set_crypto(c: CallbackQuery, state: FSMContext):
    await state.update_data(currency=c.data.split(':')[1])
    await c.message.answer('<b>💴Введите сумму в RUB:</b>')
    await TopUp.sum.set()


async def invoice(message: Message, state: FSMContext):
    if message.text.isdigit():
        config.read('config/config.ini')
        await state.update_data(sum=message.text)
        data = await state.get_data()
        payload = None
        if data['method'] == 'cryptobot':
            usd = float(get_currency())
            if 'usdt' in data['currency']:
                payload = create_invoice(float(message.text) / usd, 'usdt')
            elif 'btc' in data['currency']:
                payload = create_invoice(float(message.text) / usd / float(get_rate('bitcoin')), 'btc')
            elif 'eth' in data['currency']:
                payload = create_invoice(float(message.text) / usd / float(get_rate('ethereum')), 'eth')
            elif 'ton' in data['currency']:
                payload = create_invoice(float(message.text) / 150, 'ton')
            topup = TopUps(
                topup_id=payload['invoice_id'],
                tid=message.from_user.id,
                sum=float(data['sum']),
                type=data['method']
            )
            session.add(topup)
            session.commit()
            await message.answer('<b>Оплатите счёт по ссылке в течении 30 минут‼️:</b>',
                                 reply_markup=payload_kb(payload['pay_url'], payload['invoice_id']))
            await state.finish()
        if data['method'] == 'iban':
            topupid = random.randint(11111, 99999999)
            await message.answer(f'''<b>🧑🏼‍💻 Произведите оплату из приложения своего банка по реквизитам ниже, 
            после нажмите кнопку. Как только администрация проверит платеж - деньги зачислятся на ваш счет. 

📑 Номер счета: <code>{config["pay"]["iban"]}</code>
🕵️ Имя, Фамилия: <code>{config["pay"]["iban_fio"]}</code>
💰 Сумма: <code>{data["sum"]} EUR</code></b>''', reply_markup=iban_kb(topupid, data['sum']))
            topup = TopUps(
                topup_id=str(topupid),
                tid=message.from_user.id,
                sum=float(data['sum']),
                type=data['method']
            )
            session.add(topup)
            session.commit()
            await state.finish()
        elif data['method'] == 'qiwi':
            await message.answer('Данный метод пока не работает...')
            await state.finish()
    else:
        await state.finish()
        await message.answer('Неправильный формат')


async def check_invoice_cryptobot(c: CallbackQuery):
    try:
        topup = TopUps.query.filter(TopUps.topup_id == c.data.split(':')[1]).first()
        if '"status"' in check_invoice(topup.id):
            user = Users.query.fiter(Users.tid == c.from_user.id).first()
            user.balance_rub += topup.sum
            session.add(user)
            session.commit()
            topup.status = 'success'
            session.add(topup)
            session.commit()
            await c.message.edit_text('<b>Оплата найдена! Деньги зачислены на ваш баланс. Приятных сделок!</b>')
        else:
            await c.message.answer('<b>Оплата не найдена! Подождите и попробуйте еще раз.</b>')
    except:
        pass


async def send_notification_iban(c: CallbackQuery):
    config.read('config/config.ini')
    try:
        await c.message.bot.send_message(config['chats']['admin'],
                                         f'''
<b>Пришел платеж на IBAN от @{c.from_user.username} | ID: {c.from_user.id}
Сумма: {c.data.split(':')[2]} EUR

Подтвердите или отклоните платеж</b>''', reply_markup=iban_kb_adm(c.from_user.id, c.data.split(':')[1],
                                                                  c.data.split(':')[2]))

        await c.message.edit_text('<b>Сообщение отправлено администрации! Ожидайте подтверждения транзакции</b>')

    except:
        pass


async def cancel_invoice_crypto(c: CallbackQuery):
    await c.message.edit_text('Оплата отменена!')
    id = c.data.split(':')[1]
    order = TopUps.query.filter(TopUps.topup_id == id).first()
    order.status = 'canceled'
    session.add(order)
    session.commit()


async def cancel_iban_pay(c: CallbackQuery):
    await c.message.edit_text('Оплата отменена!')
    id = c.data.split(':')[1]
    order = TopUps.query.filter(TopUps.topup_id == id).first()
    order.status = 'canceled'
    session.add(order)
    session.commit()


def register_profile(dp: Dispatcher):
    dp.register_message_handler(my_profile, text='👑 Мой профиль', state='*', is_not_banned=True)
    dp.register_callback_query_handler(my_reviews, text='reviews', is_not_banned=True)
    dp.register_callback_query_handler(withdrawl, text='withdraw', is_not_banned=True)
    dp.register_callback_query_handler(go_req, text='qiwi_wd', is_not_banned=True)
    dp.register_callback_query_handler(go_req, text='cryptobot_wd', is_not_banned=True)
    dp.register_callback_query_handler(go_req, text='iban_wd', is_not_banned=True)
    dp.register_message_handler(set_rq, state=WD.req, is_not_banned=True)

    dp.register_callback_query_handler(top_up, text='top_up', is_not_banned=True)
    dp.register_callback_query_handler(get_method, text_contains='topup:', is_not_banned=True)
    dp.register_callback_query_handler(set_crypto, text_contains='crp:', state=TopUp.currency, is_not_banned=True)
    dp.register_message_handler(invoice, state=TopUp.sum, is_not_banned=True)
    dp.register_callback_query_handler(check_invoice_cryptobot, text_contains='paysuccess', is_not_banned=True)
    dp.register_callback_query_handler(send_notification_iban, text_contains='ibanpayready', is_not_banned=True)

    dp.register_callback_query_handler(cancel_iban_pay, text_contains='ibanpaycancel', is_not_banned=True)
    dp.register_callback_query_handler(cancel_invoice_crypto, text_contains='paycancel', is_not_banned=True)
