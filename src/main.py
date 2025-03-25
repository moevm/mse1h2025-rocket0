from datetime import datetime
from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser, CommandInfo, ArgSchema
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler, StatsHandler
from application.services import GroupService, StatsService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs, StatsArgs
from config import Config
import asyncio


def register_handlers(bot: Bot, cfg: Config) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])

    stats_service = StatsService()
    stats_handler = StatsHandler(stats_service)
    bot.register_handler(stats_handler.handle, StatsArgs, filters=[CommandFilter(Command.STATS)])

    group_service = GroupService(cfg.command_prefix)
    find_unanswered_handler = FindUnansweredHandler(cfg.user_server_url, group_service)

    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs, filters=[CommandFilter(Command.FIND_UNANSWERED)]) # noqa


def prepare_dispatcher(bots: list[Bot], cfg: Config) -> Dispatcher:
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
    }, cfg.command_prefix)

    dp = Dispatcher(bots, parser)

    return dp


if __name__ == '__main__':
    cfg = Config()
    bot = Bot(cfg.rocket_chat_url, cfg.rocket_chat_user, cfg.rocket_chat_password)
    register_handlers(bot, cfg)

    dp = prepare_dispatcher([bot], cfg)
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        print('bot stopped')
