from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser, CommandInfo, ArgSchema
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler
from application.services import GroupService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs
import asyncio
import os
from datetime import datetime


SERVER_URL = os.getenv('ROCKET_CHAT_URL')
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')


def register_handlers(bot: Bot) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])

    # здесь урла хардкодится, но в будущем можно будет прокидывать переменную окружения
    group_service = GroupService()
    find_unanswered_handler = FindUnansweredHandler("localhost:3000", group_service)
    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs, filters=[CommandFilter(Command.FIND_UNANSWERED)])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    find_unanswered_schema = {
        'hours': ArgSchema[int](int),
        'from': ArgSchema[datetime](datetime),
        'to': ArgSchema[datetime](datetime),
        'short': ArgSchema[bool](bool, default=False),
        'channels': ArgSchema[str](str, nargs='*'),
    }
    stats_schema = {
        'hours': ArgSchema[int](int),
        'from': ArgSchema[datetime](datetime),
        'to': ArgSchema[datetime](datetime),
        'channels': ArgSchema[str](str, nargs='*'),
        'users': ArgSchema[str](str, nargs='*'),
        'roles': ArgSchema[str](str, nargs='*'),
    }
    
    parser = ChatCommandParser({
        "time": CommandInfo(Command.TIME),
        "find_unanswered": CommandInfo(Command.FIND_UNANSWERED, find_unanswered_schema),
        "stats": CommandInfo(Command.STATS, stats_schema),
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
