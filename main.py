from requests import sessions
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
from dotenv import load_dotenv
import os
from pymongo import MongoClient


load_dotenv()
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')
SERVER_URL = os.getenv('ROCKET_CHAT_URL')
MONGO_URL = os.getenv('MONGO_URL_FOR_APP')

NEW_EMAIL="user@mail.ru"
NEW_NAME="NEW_USER"
NEW_PASSWORD="password"
NEW_USERNAME="testuser"


def print_start_info(rocket: RocketChat) -> None:
    pprint(rocket.me().json())
    pprint(rocket.channels_list().json())
    pprint(rocket.chat_post_message('Hello, World!', channel='GENERAL').json())
    pprint(rocket.channels_history('GENERAL', count=10).json())


def create_user(rocket: RocketChat, email: str, name: str, password: str, username: str) -> str:
    create_user_response = rocket.users_create(
        email=email,
        name=name,
        password=password,
        username=username,
        active=True, 
        roles=['user'] 
    )
    return create_user_response.json().get('user', {}).get('_id')


def print_user_info(rocket: RocketChat, id: str) -> None:
    pprint(rocket.users_info(user_id=id).json())


if __name__ == "__main__":
    with sessions.Session() as session:
        rocket = RocketChat(USERNAME, PASSWORD, SERVER_URL, session=session)
        print_start_info(rocket)
        user_id = create_user(rocket, NEW_EMAIL, NEW_NAME, NEW_PASSWORD, NEW_USERNAME)
        print_user_info(rocket, user_id)

        client = MongoClient(MONGO_URL)
        db = client['mydatabase']
        collection = db['mycollection']
        document = {"name": "ars", "age": 20}
        result = collection.insert_one(document)
        print(f"Документ вставлен с ID: {result.inserted_id}")
        client.close()
