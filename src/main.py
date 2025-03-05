from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler
from models.enums import Command
from models.dto import NoArgs
import asyncio
import os


SERVER_URL = os.getenv('ROCKET_CHAT_URL')
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')


def register_handlers(bot: Bot) -> None:
    timeHandler = TimeCommandHandler()
    bot.register_handler(timeHandler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    parser = ChatCommandParser({
        "time": Command.TIME,
    })

    dp = Dispatcher(bots, parser)

    return dp


if __name__ == '__main__':
    bot = Bot(SERVER_URL, USERNAME, PASSWORD)
    register_handlers(bot)

    dp = prepare_dispatcher([bot])
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        print('bot stopped')
