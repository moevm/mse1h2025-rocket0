from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser
from handler.filters import CommandFilter, RegexFilter, NonRepeatedFilter, NoThreadFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler, QuestionHandler
from application.services import GroupService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs
from config import Config
from logger_config import general_logger
import asyncio
import os


def register_handlers(bot: Bot) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle, NoArgs, filters=[CommandFilter(Command.TIME)])

    group_service = GroupService(config.command_prefix)
    find_unanswered_handler = FindUnansweredHandler(config.user_server_url, group_service)
    question_handler = QuestionHandler()

    bot.register_handler(find_unanswered_handler.handle, FindUnansweredArgs,
                         filters=[CommandFilter(Command.FIND_UNANSWERED)])

    # Должен регистрироваться после всех команд
    bot.register_handler(question_handler.handle, NoArgs,
                         filters=[RegexFilter(r'.*\?.*'), NonRepeatedFilter(), NoThreadFilter()])


def prepare_dispatcher(bots: list[Bot]) -> Dispatcher:
    parser = ChatCommandParser({
        "time": Command.TIME,
        "find_unanswered": Command.FIND_UNANSWERED,
    },
        config.command_prefix)

    dispatcher = Dispatcher(bots, parser)

    return dispatcher


if __name__ == '__main__':
    config = Config()
    b = Bot(config.rocket_chat_url, config.rocket_chat_user, config.rocket_chat_password)
    register_handlers(b)

    dp = prepare_dispatcher([b])
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        general_logger.info('bot stopped')
