import requests
import time
import datetime
import pytz

# Конфигурация
ROCKETCHAT_URL = "http://localhost:3000"
USER_USERNAME = "for_dump"
USER_PASSWORD = "123456"
BOT_USERNAME = "bot"
TEST_CHANNEL = "#questions_2"

def login(username, password):
    response = requests.post(f"{ROCKETCHAT_URL}/api/v1/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()['data']['authToken'], response.json()['data']['userId']
    else:
        raise Exception("Ошибка аутентификации: " + response.json().get('error'))

def send_message(auth_token, user_id, message):
    response = requests.post(f"{ROCKETCHAT_URL}/api/v1/chat.postMessage", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    }, json={
        "channel": TEST_CHANNEL,
        "text": message
    })
    return response

def get_bot_response(auth_token, user_id):
    time.sleep(5)  # Увеличиваем время ожидания для получения ответа от бота
    room_id = get_room_id(auth_token, user_id)
    
    if not room_id:
        print("Канал не найден.")
        return None

    response = requests.get(f"{ROCKETCHAT_URL}/api/v1/channels.history", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    }, params={"roomId": room_id})

    if response.status_code == 200:
        messages = response.json()['messages']
        for message in messages:
            if message['u']['username'] == BOT_USERNAME:
                return message['msg']
    return None

def get_room_id(auth_token, user_id):
    response = requests.get(f"{ROCKETCHAT_URL}/api/v1/channels.list", headers={
        "X-Auth-Token": auth_token,
        "X-User-Id": user_id
    })
    
    if response.status_code == 200:
        channels = response.json()['channels']
        for channel in channels:
            if channel['name'] == TEST_CHANNEL.lstrip('#'):
                return channel['_id']
    
    return None

def test_time_command():
    try:
        auth_token, user_id = login(USER_USERNAME, USER_PASSWORD)
        
        # Отправляем команду !time
        send_message(auth_token, user_id, "!time")
        
        # Получаем ответ от бота
        bot_response = get_bot_response(auth_token, user_id)
        
        if bot_response is None:
            print("Бот не ответил.")
            return
        
        # Проверяем формат ответа
        print(f"Ответ бота: '{bot_response}'")  # Отладочная информация
        
        # Извлекаем дату и время из ответа
        try:
            bot_time_full = datetime.datetime.strptime(bot_response.strip(), "Текущее время: %Y-%m-%d %H:%M:%S")
            print(f"Парсинг времени прошел успешно: {bot_time_full}")  # Отладочная информация
            
            # Предполагаем, что время от бота в UTC
            bot_time_full = bot_time_full.replace(tzinfo=pytz.UTC)
            
            # Получаем текущее время в UTC
            current_time = datetime.datetime.now(pytz.UTC)
            time_difference = abs((bot_time_full - current_time).total_seconds())
            print(f"Текущее время: {current_time}, Разница во времени: {time_difference} секунд")  # Отладочная информация
            
            assert time_difference <= 300  # 300 секунд = 5 минут
            
            print("Тест для команды '!time' пройден успешно!")
        
        except ValueError as ve:
            print(f"Ошибка парсинга времени: {ve}")
            print(f"Ответ бота '{bot_response}' не соответствует ожидаемому формату времени.")
    
    except Exception as e:
        print("Ошибка:", str(e))

def main():
    test_time_command()

if __name__ == "__main__":
    main()