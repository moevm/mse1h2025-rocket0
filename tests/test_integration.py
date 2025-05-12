import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import Bot 
from models.enums import RoomType 

class TestBot(unittest.TestCase):

    @patch('bot.RocketChatAsync')
    @patch('bot.RocketChat')
    def setUp(self, MockRocketChat, MockRocketChatAsync):
        self.mock_sync_client = MockRocketChat.return_value
        self.mock_async_client = MockRocketChatAsync.return_value
        
        self.bot = Bot(server_url='localhost', username='test_user', password='test_password')
        self.bot.sync_client = self.mock_sync_client
        self.bot.async_client = self.mock_async_client

    @patch('asyncio.sleep', new_callable=AsyncMock)  # Мокаем asyncio.sleep для асинхронных тестов
    async def test_send_message(self):
        channel_id = 'channel_id'
        text = 'Hello, World!'
        
        await self.bot.send_message(text, channel_id)
        self.mock_async_client.send_message.assert_called_once_with(text, channel_id, None)

    async def test_get_channels(self):
        self.mock_async_client.get_channels_raw.return_value = [
            {"_id": "channel_id_1", "t": "c", "name": "general"},
            {"_id": "channel_id_2", "t": "d", "name": "direct"},
        ]
        
        channels = await self.bot.get_channels()
        
        expected_channels = [
            {"_id": "channel_id_1", "t": RoomType.CHANNEL.value, "name": "general"},
            {"_id": "channel_id_2", "t": RoomType.DIRECT.value, "name": "direct"},
        ]
        
        self.assertEqual(channels, expected_channels)

    def test_get_channel_history(self):
        channel_id = 'channel_id'
        
        self.mock_sync_client.channels_history.return_value.status_code = 200
        self.mock_sync_client.channels_history.return_value.json.return_value = {
            'messages': [],
            'success': True,
            'total': 0,
        }
        
        history = self.bot.get_channel_history(channel_id)
        
        self.mock_sync_client.channels_history.assert_called_once_with(channel_id, count=0, offset=0)
        
        # Проверяем результат
        self.assertEqual(history['messages'], [])
    
if __name__ == '__main__':
    unittest.main()