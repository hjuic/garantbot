from aiogram.types import Message
from configparser import ConfigParser
from keyboards.kb import *
from aiogram import Dispatcher

config = ConfigParser()


async def help_msg(msg: Message):
    config.read('config/config.ini')
    await msg.answer_photo(photo='https://it-tehnik.ru/wp-content/uploads/podderzhka-telegram.jpg',
                           caption='<b>Помощь:</b>', reply_markup=help_kb(config['chats']['support']))


async def get_photo_id(msg: Message):
    document_id = msg.photo[0].file_id
    file_info = await msg.bot.get_file(document_id)
    print(f'file_id: {file_info.file_id}')
    print(f'file_path: {file_info.file_path}')
    print(f'file_size: {file_info.file_size}')
    print(f'file_unique_id: {file_info.file_unique_id}')


async def our_projects(message: Message):
    await message.answer_photo(
        photo='https://teknokuys.com/wp-content/uploads/2021/01/Bot-Telegram-yang-manfaat.jpg',
        caption='<b>Все актуальные ссылки на наши проекты🌪️</b>',
        reply_markup=our_pr())


def reg_help(dp: Dispatcher):
    dp.register_message_handler(help_msg, text='⛑ Помощь', state='*', is_not_banned=True)
    dp.register_message_handler(get_photo_id, content_types=['photo'], is_not_banned=True)
    dp.register_message_handler(our_projects, text='📒 Наши проекты', is_not_banned=True)
