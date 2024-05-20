import logging
import sys
from os import getenv
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from a0_config import TOKEN, BASE_WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_SERVER_HOST, WEB_SERVER_PORT
from a2_handlers import router
from a3_error_handlers import router as error_router



async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

async def on_shutdown(bot: Bot) -> None:
    print("bot has been stopped")


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)
    dp.include_router(error_router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    print("-------------------")
    print("web server host: ", WEB_SERVER_HOST)
    print("web server port: ", WEB_SERVER_PORT)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    print('LETS GOOOO')
    print('LETS GOOOO')
    print('LETS GOOOO')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()