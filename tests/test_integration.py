import requests
import time

# Конфигурация
ROCKETCHAT_URL = "http://localhost:3000"  # URL вашего Rocket.Chat
USER_USERNAME = "for_dump"  # Имя пользователя для отправки сообщения
USER_PASSWORD = "123456"  # Пароль пользователя
BOT_USERNAME = "bot"            # Имя пользователя бота
TEST_CHANNEL = "#questions_2"                # Канал для тестирования
TEST_MESSAGE = "!time"                 # Сообщение, отправляемое пользователем

def login(username, password):
    """Аутентификация пользователя и получение токена."""
    response = requests.post(f"{ROCKETCHAT_URL}/api/v1/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()['data']['authToken'], response.json()['data']['userId']
    else:
        raise Exception("Ошибка аутентификации: " + response.json().get('error'))

def send_message(auth_token, user_id, message):
    """Отправка сообщения в указанный канал."""
    response = requests.post(f"{ROCKETCHAT_URL}/api/v1/chat.postMessage", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    }, json={
        "channel": TEST_CHANNEL,
        "text": message
    })
    return response

def get_room_id(auth_token, user_id, channel_name):
    """Получение roomId по имени канала."""
    response = requests.get(f"{ROCKETCHAT_URL}/api/v1/channels.list", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    })
    
    if response.status_code == 200:
        channels = response.json()['channels']
        print("Доступные каналы:")
        for channel in channels:
            print(f"- {channel['name']} (ID: {channel['_id']})")  # Выводим имя и ID канала
        for channel in channels:
            if channel['name'] == channel_name.lstrip('#'):
                return channel['_id']
    else:
        print("Ошибка при получении списка каналов:", response.text)
    
    return None

def check_bot_response(auth_token, user_id):
    """Проверка ответа бота на сообщение."""
    time.sleep(5)  # Увеличиваем время ожидания

    room_id = get_room_id(auth_token, user_id, TEST_CHANNEL)
    
    if not room_id:
        print("Канал не найден.")
        return None

    # Получаем последние сообщения из канала
    response = requests.get(f"{ROCKETCHAT_URL}/api/v1/channels.history", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    }, params={"roomId": room_id})
    
    print("Статус код:", response.status_code)
    print("Ответ:", response.text)  # Выводим текст ответа для диагностики

    if response.status_code == 200:
        messages = response.json()['messages']
        for message in messages:
            if message['u']['username'] == BOT_USERNAME:
                return message['msg']  # Возвращаем ответ бота
    return None

def main():
    try:
        # Аутентификация пользователя
        user_auth_token, user_id = login(USER_USERNAME, USER_PASSWORD)
        
        # Отправляем сообщение от пользователя
        send_message(user_auth_token, user_id, TEST_MESSAGE)
        
        # Проверяем ответ бота (аутентификация бота не требуется для проверки ответа)
        bot_response = check_bot_response(user_auth_token, user_id)
        
        if bot_response:
            print("Ответ бота:", bot_response)
            print("Тест пройден успешно! Бот ответил.")
            sys.exit(1) 
        else:
            print("Бот не ответил на сообщение.")
    
    except Exception as e:
        print("Ошибка:", str(e))

if __name__ == "__main__":
    main()