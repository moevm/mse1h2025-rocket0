from requests import sessions
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat
from dotenv import load_dotenv
import os


load_dotenv()
USERNAME = os.getenv('ROCKET_CHAT_USER')
PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')
SERVER_URL = os.getenv('ROCKET_CHAT_URL')

NEW_USER_EMAIL="user1@mail.ru"
NEW_USER_NAME="NEW_USER1"
NEW_USER_PASSWORD="password1"
NEW_USER_USERNAME="testuser1"


if __name__ == "__main__":
    with sessions.Session() as session:
        rocket = RocketChat(USERNAME, PASSWORD, SERVER_URL, session=session)
        pprint(rocket.me().json())
        pprint(rocket.channels_list().json())
        pprint(rocket.chat_post_message('Hello, World!', channel='GENERAL').json())
        pprint(rocket.channels_history('GENERAL', count=5).json())

        create_user_response = rocket.users_create(
            email=NEW_USER_EMAIL,
            name=NEW_USER_NAME,
            password=NEW_USER_PASSWORD,
            username=NEW_USER_USERNAME,
            active=True, 
            roles=['user'] 
        )
        pprint(create_user_response.json())

        new_user_id = create_user_response.json().get('user', {}).get('_id')    
        print(f"New user created with ID: {new_user_id}")
        user_info_response = rocket.users_info(user_id=new_user_id)
        pprint(user_info_response.json())
