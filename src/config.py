from dataclasses import dataclass, field
import os


@dataclass
class Config:
    env_type: str = field(default=os.getenv("ENV_TYPE", "dev"))
    rocket_chat_user: str = field(default=os.getenv("ROCKET_CHAT_USER"))
    rocket_chat_password: str = field(default=os.getenv("ROCKET_CHAT_PASSWORD"))
    rocket_chat_url: str = field(default=os.getenv("ROCKET_CHAT_URL"))
    mongo_url_for_app: str = field(default=os.getenv("MONGO_URL_FOR_APP"))
    command_prefix: str = "!"
    service_reactions: frozenset[str] = frozenset((":gear:",))
    user_server_url: str = field(default=os.getenv("ROCKET_CHAT_URL"))
    privileged_roles: frozenset[str] = field(
        default=frozenset(os.getenv("PRIVILEGED_ROLES", "admin").replace(" ", "").split(",")))
    telegram_token: str = field(default=os.getenv("TELEGRAM_TOKEN"))
    telegram_users_allow_list: frozenset[int] = field(
        default=frozenset(map(int, os.getenv("TELEGRAM_USERS_ALLOW_LIST", "").replace(" ", "").split(","))))

    def __post_init__(self):
        if self.env_type in ("dev", ""):
            self.user_server_url = self.rocket_chat_url.replace("host.docker.internal", "localhost")
