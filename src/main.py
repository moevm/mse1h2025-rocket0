from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler
from application.services import GroupService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs, Config
import asyncio
import os


SERVER_URL = os.getenv('ROCKET_CHAT_URL')
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')


def register_handlers(bot: Bot) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])

    # здесь урла хардкодится, но в будущем можно будет прокидывать переменную окружения
    group_service = GroupService(config.prefix)
    find_unanswered_handler = FindUnansweredHandler(config.server_url, group_service)
    
    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs, filters=[CommandFilter(Command.FIND_UNANSWERED)])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    parser = ChatCommandParser({
        "time": Command.TIME,
        "find_unanswered": Command.FIND_UNANSWERED,
    }, 
    config.prefix)
    
    dp = Dispatcher(bots, parser)

    return dp


if __name__ == '__main__':
    config = Config(prefix="!", server_url="localhost:3000")
    bot = Bot(SERVER_URL, USERNAME, PASSWORD)
    register_handlers(bot)

    dp = prepare_dispatcher([bot])
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        print('bot stopped')
