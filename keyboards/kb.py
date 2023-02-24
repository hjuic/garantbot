from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def accept():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('✅ Ознакомлен с правилами', callback_data='accept')
    )

    return keyboard


def menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add('👑 Мой профиль')
    keyboard.add('♻ Мои сделки', '➕ Новая сделка')
    keyboard.add('⛑ Помощь', '📒 Наши проекты')

    return keyboard


def profile():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('📥 Пополнить', callback_data='top_up'),
        InlineKeyboardButton('📤 Вывести', callback_data='withdraw'),
        InlineKeyboardButton('📃 Мои отзывы', callback_data='reviews')
    )
    return keyboard


def withdraw_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        #InlineKeyboardButton('QIWI (RUB)', callback_data='qiwi_wd'),
        InlineKeyboardButton('CryptoBot чек (RUB)', callback_data='cryptobot_wd'),
        #InlineKeyboardButton('IBAN (EURO)', callback_data='iban_wd')
    )
    return keyboard


def admin_wd(tid):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('Обработано', callback_data=f'okwithd:{tid}'),
        InlineKeyboardButton('Отказано', callback_data=f'nowithd:{tid}')
    )
    return keyboard


def top_up_method():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        #InlineKeyboardButton('QIWI', callback_data='topup:qiwi'),
        #InlineKeyboardButton('IBAN', callback_data='topup:iban'),
        InlineKeyboardButton('CryptoBot', callback_data='topup:cryptobot')
    )

    return keyboard


def set_crypto_():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton('USDT', callback_data='crp:usdt'),
        InlineKeyboardButton('BTC', callback_data='crp:btc'),
        InlineKeyboardButton('ETH', callback_data='crp:eth'),
        InlineKeyboardButton('TON', callback_data='crp:ton')
    )
    return keyboard


def payload_kb(url, id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('Оплатить💸', url=url)
    )
    keyboard.add(
        InlineKeyboardButton('Оплатил♻', callback_data=f'paysuccess:{id}'),
        InlineKeyboardButton('Отменить❌', callback_data=f'paycancel:{id}')
    )

    return keyboard


def iban_kb(id, sum):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('Оплатил♻', callback_data=f'ibanpayready:{id}:{sum}'),
        InlineKeyboardButton('Отменить❌', callback_data=f'ibanpaycancel:{id}')
    )
    return keyboard


def iban_kb_adm(tid, id, sum):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('Зачислить юзеру', callback_data=f'ibansuccess:{id}:{sum}:{tid}'),
        InlineKeyboardButton('Отказать (Платеж не пришел)', callback_data=f'ibancancell:{id}:{sum}:{tid}')
    )

    return keyboard


def help_kb(support):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('Админ 🎓', url='https://t.me/voplopoll'),
        InlineKeyboardButton('Поддержка ⛑️', url=f'https://t.me/hjuic_support'),
        InlineKeyboardButton('Правила 📖', url='https://telegra.ph/Pravila-polzovaniya-hjuic-garantbot-02-10')
    )
    return kb


def menu_orders():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        # InlineKeyboardButton('Начать сделку', callback_data='find_user'),
        InlineKeyboardButton('🔓 Активные сделки', callback_data='activedeals'),
        InlineKeyboardButton('🔐 Завершенные сделки', callback_data='success_orders')
    )
    return keyboard


def seller_kb(tid):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('🤝 Предложить сделку', callback_data=f'requestdeal:{tid}'),
        InlineKeyboardButton('🗂️ Посмотреть отзывы', callback_data=f'showreviews:{tid}')
    )
    return keyboard


def confirm_request():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('✅ Подтвердить', callback_data='startdeal'),
        InlineKeyboardButton('❌ Отменить', callback_data='cancelrequest')
    )

    return keyboard


def accept_request(id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton('✅ Принять запрос', callback_data=f'acceptdeal:{id}'),
        InlineKeyboardButton('❌ Отклонить запрос', callback_data=f'declinedeal:{id}')
    )

    return keyboard


def menu_of_deal_seller(id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('❓ Открыть спор', callback_data=f'arbitr:{id}'),
        InlineKeyboardButton('❌ Отменить сделку', callback_data=f'canceldeal:{id}')
    )

    return keyboard


def menu_of_deal_buyer(id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('♻ Завершить сделку', callback_data=f'closedeal:{id}'),
        InlineKeyboardButton('❓ Открыть спор', callback_data=f'arbitr:{id}')
    )

    return keyboard


def confirmclosee(id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Подтвердить', callback_data=f'confirmclose:{id}'),
        InlineKeyboardButton('Отменить', callback_data=f'cancelclose:{id}')
    )

    return keyboard


def give_review(id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Оставить отзыв', callback_data=f'givereview:{id}')
    )
    return keyboard


def type_deal():
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton('📤 Продажи', callback_data='selldeal'),
        InlineKeyboardButton('📥 Покупки', callback_data='buydeal')
    )

    return keyboard


def list_deals(u):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i in u:
        keyboard.add(
            InlineKeyboardButton(f'Сделка №{i.order_id}', callback_data=f'mydeal:{i.order_id}')
        )
    return keyboard


def confirm_arbitr(id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Подтвердить', callback_data=f'arbitr_confirm:{id}'),
        InlineKeyboardButton('Отменить', callback_data=f'arbitr_cancel:{id}')
    )

    return keyboard


def confirmcanceldeal(id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('Подтвердить', callback_data=f'confirmcancelldeal:{id}'),
        InlineKeyboardButton('Отменить действие', callback_data=f'cancelcancelldeal:{id}')
    )

    return keyboard


def chose_s():
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton('📤 Продажи', callback_data='s_sell_deal'),
        InlineKeyboardButton('📥 Покупки', callback_data='s_buy_deal')
    )

    return keyboard


def list_deals_s(u):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i in u:
        keyboard.add(
            InlineKeyboardButton(f'Сделка №{i.order_id}', callback_data=f'mydealss:{i.order_id}')
        )
    return keyboard


def panel_of_user(tid):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton('Заблокировать', callback_data=f'banuser:{tid}'),
        InlineKeyboardButton('Разблокировать', callback_data=f'unban:{tid}'),
        InlineKeyboardButton('Добавить баланс', callback_data=f'addbalance:{tid}')
    )
    return keyboard


def our_pr():
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton('Чат💬', url='https://t.me/+TW3FOOc4MFIxOGRi'),
        InlineKeyboardButton('Канал📊', url='https://t.me/+xM5YABs5DrI1NTVi'),
        InlineKeyboardButton('Здесь уже готовится что-то новое⚒', callback_data='llllllld;d;d;d;d;d')
    )

    return keyboard


def admin_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('🔍 Поиск пользователя', callback_data='findadmin'),
        InlineKeyboardButton('✉ Запустить рассылку', callback_data='say'),
        InlineKeyboardButton('📊 Платежные данные', callback_data='changeplatezh'),
        InlineKeyboardButton('🪙 Изменить контакт саппорта', callback_data='changesupport')
    )
    return keyboard


def dispute_admin(buyer, seller, order_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('В сторону продавца', callback_data=f'seller:{seller}:{buyer}:{order_id}'),
        InlineKeyboardButton('В сторону покупателя', callback_data=f'buyer:{buyer}:{seller}:{order_id}')
    )
    return keyboard
