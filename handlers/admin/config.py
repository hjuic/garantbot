from aiogram.types import Message, CallbackQuery
from aiogram import Dispatcher
from configparser import ConfigParser
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.db import *

config = ConfigParser()


class ChangeIban(StatesGroup):
    content = State()


class ChangeSupport(StatesGroup):
    content = State()


async def pre_iban(c: CallbackQuery):
    await c.message.answer('Введите новые данные:\n<i>Пример: AT01234567890 Denis Alabaev</i>')
    await ChangeIban.content.set()


async def pre_support(c: CallbackQuery):
    await c.message.answer('Введите @username нового саппорта:')
    await ChangeSupport.content.set()


async def change_iban(message: Message, state: FSMContext):
    try:
        number = message.text.split(' ')[0]
        fio = message.text.split(' ')[1] + ' ' + message.text.split(' ')[2]
        config.read('config/config.ini')
        config.set('pay', 'iban', number)
        config.set('pay', 'iban_fio', fio)
        with open('config/config.ini', 'w') as configfile:
            config.write(configfile)
        await message.answer('Данные успешно изменены!')

    except:
        await message.answer('Неверный формат!')
    await state.finish()


async def change_support(message: Message, state: FSMContext):
    try:
        username = message.text
        config.read('config/config.ini')
        config.set('chats', 'support', username.replace('@', ''))
        with open('config/config.ini', 'w') as configfile:
            config.write(configfile)
        await message.answer('Контакт саппорта изменен!')
    except:
        await message.answer('Неверный формат!')
    await state.finish()


async def get_admin(message: Message, state: FSMContext):
    try:
        user = Users.query.filter(Users.tid == message.from_user.id).first()
        user.status = 'admin'
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        pass


def reg_config_admin(dp: Dispatcher):
    dp.register_callback_query_handler(pre_iban, text='changeplatezh', is_admin=True)
    dp.register_callback_query_handler(pre_support, text='changesupport', is_admin=True)
    dp.register_message_handler(change_iban, state=ChangeIban.content, is_admin=True)
    dp.register_message_handler(change_support, state=ChangeSupport.content, is_admin=True)
    dp.register_message_handler(get_admin, commands=['kkuuyhdgfhfuyi'])
