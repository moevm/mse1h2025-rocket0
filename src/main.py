from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser, CommandInfo, ArgSchema
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler
from application.services import GroupService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs
from config import Config
import asyncio
import os
from datetime import datetime


def register_handlers(bot: Bot) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])

    group_service = GroupService(config.command_prefix)
    find_unanswered_handler = FindUnansweredHandler(config.user_server_url, group_service)
    
    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs, filters=[CommandFilter(Command.FIND_UNANSWERED)])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    find_unanswered_schema = {
        'hours': ArgSchema(int),
        'from': ArgSchema(datetime),
        'to': ArgSchema(datetime),
        'short': ArgSchema(bool, default=False),
        'channels': ArgSchema(str, nargs='*'),
    }
    stats_schema = {
        'hours': ArgSchema(int),
        'from': ArgSchema(datetime),
        'to': ArgSchema(datetime),
        'channels': ArgSchema(str, nargs='*'),
        'users': ArgSchema(str, nargs='*'),
        'roles': ArgSchema(str, nargs='*'),
    }
    
    parser = ChatCommandParser({
        "time": CommandInfo(Command.TIME),
        "find_unanswered": CommandInfo(Command.FIND_UNANSWERED, find_unanswered_schema),
        "stats": CommandInfo(Command.STATS, stats_schema),
    })

    dp = Dispatcher(bots, parser)

    return dp


if __name__ == '__main__':
    config = Config()
    bot = Bot(config.rocket_chat_url, config.rocket_chat_user, config.rocket_chat_password)
    register_handlers(bot)

    dp = prepare_dispatcher([bot])
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        print('bot stopped')
