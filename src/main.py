from datetime import datetime
from dispatcher import Dispatcher, Bot
from parsers import ChatCommandParser, CommandInfo, ArgSchema
from handler.filters import CommandFilter, RoleFilter, RegexFilter, NonRepeatedFilter, NoThreadFilter
from application.handlers import TimeCommandHandler, FindUnansweredHandler, StatsHandler, QuestionHandler, FindMessageHandler
from application.services import ChannelService, StatsService
from models.enums import Command
from models.dto import NoArgs, FindUnansweredArgs, StatsArgs, FindMessageArgs
from config import Config
from logger_config import general_logger, add_telegram_handler
import asyncio


def register_handlers(bot: Bot, cfg: Config) -> None:
    time_handler = TimeCommandHandler()
    bot.register_handler(time_handler.handle,
                         NoArgs,
                         filters=[CommandFilter(Command.TIME), RoleFilter(cfg.privileged_roles)])

    stats_service = StatsService()
    stats_handler = StatsHandler(stats_service)
    bot.register_handler(stats_handler.handle,
                         StatsArgs, 
                         filters=[CommandFilter(Command.STATS), RoleFilter(cfg.privileged_roles)])

    channel_service = ChannelService(cfg.command_prefix, cfg.service_reactions, cfg.privileged_roles)
    find_unanswered_handler = FindUnansweredHandler(cfg.user_server_url, channel_service)

    bot.register_handler(find_unanswered_handler.handle,
                         FindUnansweredArgs,
                         filters=[CommandFilter(Command.FIND_UNANSWERED), RoleFilter(cfg.privileged_roles)])
    
    find_message_handler = FindMessageHandler(cfg.user_server_url, channel_service)
    bot.register_handler(find_message_handler.handle,
                         FindMessageArgs,
                         filters=[CommandFilter(Command.FIND_MESSAGE), NonRepeatedFilter(), RoleFilter(cfg.privileged_roles)])

    # Должен регистрироваться после всех команд
    question_handler = QuestionHandler()
    bot.register_handler(question_handler.handle, NoArgs,
                         filters=[RegexFilter(r'.*\?.*'), NonRepeatedFilter(), NoThreadFilter()])


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
    find_message_schema = {
        'pattern': ArgSchema(str, positional=True)
    }

    parser = ChatCommandParser({
        "time": CommandInfo(Command.TIME),
        "find_unanswered": CommandInfo(Command.FIND_UNANSWERED, find_unanswered_schema),
        "stats": CommandInfo(Command.STATS, stats_schema),
        "find_message": CommandInfo(Command.FIND_MESSAGE, find_message_schema),
    }, cfg.command_prefix)

    dispatcher = Dispatcher(bots, parser)

    return dispatcher


if __name__ == '__main__':
    config = Config()

    if len(config.telegram_token) > 0:
        add_telegram_handler(config.telegram_token, list(config.telegram_users_allow_list))

    b = Bot(config.rocket_chat_url, config.rocket_chat_user, config.rocket_chat_password)
    register_handlers(b, config)

    dp = prepare_dispatcher([b], config)
    try:
        asyncio.run(dp.start_polling())
    except KeyboardInterrupt:
        general_logger.info('bot stopped')
