from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser, ArgShema
from handler.filters import CommandFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler
from application.services import GroupService
from models.enums import Command, TypeOption
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
    find_unanswered_shema = {
        'hours': ArgShema(int, required=False, choices=range(0, 72), conflicts_with=['from']),
        'from': ArgShema(datetime, required=False, conflicts_with=['hours']),
        'to': ArgShema(datetime, required=False, depends_on=['from']),
        'short': ArgShema(bool,required=False, default=False),
        'channel': ArgShema(str, required=False, default='all')
        
        # '__meta__': {
        #     'one_required': [['hours', 'from']]
        # }
    }
    get_statistics_shema = {
        'hours': ArgShema(int, required=False, choices=range(0, 72), conflicts_with=['from']),
        'from': ArgShema(datetime, required=False, conflicts_with=['hours']),
        'to': ArgShema(datetime, required=False, depends_on=['from']),
        'type': ArgShema(type_=TypeOption, required=False, default=TypeOption.ALL),
    }
    get_user_statistics_shema = {
        'hours': ArgShema(int, required=False, choices=range(0, 72), conflicts_with=['from']),
        'from': ArgShema(datetime, required=False, conflicts_with=['hours']),
        'to': ArgShema(datetime, required=False, depends_on=['from']),
        'login': ArgShema(str, required=True),
    }
    
    parser = ChatCommandParser({
        "time": Command.TIME,
        "find_unanswered": Command.FIND_UNANSWERED,
        "get_statistics": Command.GET_STATISTICS,
        "get_user_statistics": Command.GET_USER_STATISTICS,
    }, {
        Command.FIND_UNANSWERED: find_unanswered_shema,
        Command.GET_STATISTICS: get_statistics_shema,
        Command.GET_USER_STATISTICS: get_user_statistics_shema,
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
