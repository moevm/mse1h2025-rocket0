from requests import sessions
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
from dotenv import load_dotenv
import os


USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')
SERVER_URL = os.getenv('ROCKET_CHAT_URL')


if __name__ == "__main__":
    with sessions.Session() as session:
        rocket = RocketChat(USERNAME, PASSWORD, SERVER_URL, session=session)
        pprint(rocket.me().json())
        pprint(rocket.channels_list().json())
        pprint(rocket.chat_post_message('Hello, World!', channel='GENERAL').json())
        pprint(rocket.channels_history('GENERAL', count=5).json())
