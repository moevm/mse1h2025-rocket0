import unittest
import asyncio
import sys
import os

# Добавляем путь к src в системный путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from dispatcher.bot import Bot  # Импортируем класс Bot из нужного модуля

class IntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_url = 'localhost:3000'  # Укажите адрес вашего сервера Rocket.Chat
        cls.username = 'your_username'       # Укажите имя пользователя
        cls.password = 'your_password'       # Укажите пароль

        cls.bot = Bot(cls.server_url, cls.username, cls.password)

    def test_connect(self):
        """Проверка подключения к Rocket.Chat."""
        loop = asyncio.get_event_loop()
        connected = loop.run_until_complete(self.bot.async_client.start(f'ws://{self.server_url}/websocket', self.username, self.password))
        self.assertTrue(connected, "Bot failed to connect to Rocket.Chat")

    def test_get_channels(self):
        """Проверка получения списка каналов."""
        loop = asyncio.get_event_loop()
        channels = loop.run_until_complete(self.bot.get_channels())
        
        self.assertIsInstance(channels, list, "Channels should be a list")
        self.assertGreater(len(channels), 0, "Channels list should not be empty")

    def test_send_message(self):
        """Проверка отправки сообщения в канал."""
        loop = asyncio.get_event_loop()
        
        # Предположим, что у вас есть канал с ID 'general'
        channel_id = 'general'
        message_text = 'Hello from the bot!'
        
        send_result = loop.run_until_complete(self.bot.send_message(message_text, channel_id))
        
        self.assertIsNone(send_result, "Message sending should not return an error")

    def test_get_channel_history(self):
        """Проверка получения истории сообщений канала."""
        loop = asyncio.get_event_loop()
        
        # Предположим, что у вас есть канал с ID 'general'
        channel_id = 'general'
        
        history = loop.run_until_complete(self.bot.get_channel_history(channel_id))
        
        self.assertIn('messages', history, "History response should contain messages")
    
if __name__ == '__main__':
    unittest.main()