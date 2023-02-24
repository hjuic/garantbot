import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configparser import ConfigParser
from handlers.start import register_start
from handlers.users.profile import register_profile
from handlers.admin.topup import register_admin_topup
from handlers.users.help import reg_help
from handlers.users.orders.main import register_main_deal
from handlers.users.orders.my_deal import reg_my_deal
from handlers.users.orders.review import reg_review
from handlers.users.orders.successdeals import reg_success
from handlers.admin.user_panel import reg_user_admin
from handlers.admin.config import reg_config_admin
from filters.is_admin import IsAdmin
from filters.is_not_banned import IsNotBanned
from handlers.admin.main import register_admin_menu
from handlers.admin.say import reg_say_admin

config = ConfigParser()
config.read('config/config.ini')

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO
    )
    logging.error('Bot starting..')

    storage = MemoryStorage()

    bot = Bot(token=config['bot']['token'], parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsNotBanned)

    register_start(dp)
    register_profile(dp)
    register_admin_topup(dp)
    reg_help(dp)
    reg_my_deal(dp)
    register_main_deal(dp)
    reg_review(dp)
    reg_success(dp)
    reg_user_admin(dp)
    reg_config_admin(dp)
    register_admin_menu(dp)
    reg_say_admin(dp)

    try:
        await dp.start_polling()

    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


def cli():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped by User')


if __name__ == '__main__':
    cli()
