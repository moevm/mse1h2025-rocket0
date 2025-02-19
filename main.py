from datetime import datetime
from rocketchat_API.rocketchat import RocketChat
from rocketchat_async import RocketChat as RocketChatAsync
import asyncio
from dotenv import load_dotenv
import os


class RocketChatBot:
    def __init__(self, server_url: str, username: str, password: str, command_prefix: str = '!'):
        self.server_url: str = server_url
        self.username: str = username
        self.password: str = password
        self.command_prefix: str = command_prefix

        # TODO: http должно меняться на https, а ws на wss
        self.async_client: RocketChatAsync = RocketChatAsync()
        self.sync_client: RocketChat = RocketChat(username, password, server_url=f'http://{server_url}')

        self.commands = {}
        self.my_id = None

    def register_command(self, command: str, handler, description: str = ''):
        self.commands[command] = {'handler': handler, 'description': description}

    async def handle_command(self, command, args, message):
        if command in self.commands:
            try:
                await self.commands[command]['handler'](args, message)
            except Exception as e:
                print(f'Ошибка при выполнении команды {command}: {e}')
                await self.async_client.send_message('Произошла ошибка при выполнении команды.', message['rid'])
        else:
            await self.async_client.send_message('Неизвестная команда.', message['rid'])

    async def command_time(self, args, message):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await self.async_client.send_message(f'Текущее время: {current_time}', message['rid'])

    def message_callback(self, message):
        asyncio.create_task(self.process_message(message))

    async def process_message(self, message):
        if 'msg' not in message:
            return

        text = message['msg']

        # Игнорируем свои сообщения, в идеале нужно игнорировать и других ботов.
        if 'u' in message and message['u'].get('_id') == self.my_id:
            return

        if text.startswith(self.command_prefix):
            parts = text[len(self.command_prefix):].split()
            if parts:
                command = parts[0]
                args = parts[1:]
                await self.handle_command(command, args, message)

    async def run(self):
        me_response = self.sync_client.me().json()
        self.my_id = me_response.get('_id')

        self.register_command('time', self.command_time, 'Узнать текущее время')

        attempts: int = 5
        while attempts > 0:
            try:
                await self.async_client.start(f'ws://{self.server_url}/websocket', self.username, self.password)

                for channel_id, channel_type in await self.async_client.get_channels():
                    await self.async_client.subscribe_to_channel_messages_raw(channel_id, self.message_callback)

                await self.async_client.run_forever()
            except (RocketChatAsync.ConnectionClosed,
                    RocketChatAsync.ConnectCallFailed) as e:
                print(f'Connection failed: {e}. Waiting a few seconds...')
                await asyncio.sleep(3)
                print('Reconnecting...')
                attempts -= 1


if __name__ == '__main__':
    load_dotenv()
    SERVER_URL = os.getenv('ROCKET_CHAT_URL')
    USERNAME = os.getenv('ROCKET_CHAT_USER')
    PASSWORD = os.getenv('ROCKET_CHAT_PASSWORD')

    bot = RocketChatBot(SERVER_URL, USERNAME, PASSWORD)
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print('bot stopped')
