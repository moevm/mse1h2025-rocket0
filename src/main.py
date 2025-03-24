from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler
from application.services import GroupService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs
import asyncio
import os
from application.handlers.stats_handler import StatsHandler
from application.services.stats_service import StatsService
from models.dto.stats import StatsArgs

SERVER_URL = os.getenv('ROCKET_CHAT_URL')
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')


def register_handlers(bot: Bot) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[
                         CommandFilter(Command.TIME)])

    stats_service = StatsService()
    stats_handler = StatsHandler(stats_service)
    bot.register_handler(stats_handler.handle, StatsArgs,
                         filters=[CommandFilter(Command.STATS)])

    # здесь урла хардкодится, но в будущем можно будет прокидывать переменную окружения
    group_service = GroupService()
    find_unanswered_handler = FindUnansweredHandler(
        "localhost:3000", group_service)
    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs, filters=[
                         CommandFilter(Command.FIND_UNANSWERED)])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    parser = ChatCommandParser({
        "time": Command.TIME,
        "find_unanswered": Command.FIND_UNANSWERED,
        "stats": Command.STATS
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
