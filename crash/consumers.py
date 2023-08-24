import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from .gamemanager import GameManager  # Import the GameManager class from a separate file

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'realtime_group'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        self.game_manager = GameManager.get_instance()

        # Add this consumer to the GameManager instance
        await self.game_manager.add_consumer(self)

        

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove this consumer from the GameManager instance
        self.game_manager.remove_consumer(self)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', '')

        if message_type == "crash_instruction":
            await self.handle_crash_instruction(data)
        elif message_type == "start_synchronizer":
            await self.handle_start_synchronizer(data)
        elif message_type == "ongoing_synchronizer":
            await self.handle_ongoing_synchronizer(data)

    async def handle_crash_instruction(self, data):
        # Handle crash instruction here, e.g., trigger the crash action in the game
        await self.send(text_data=json.dumps({
            'message': 'Crash instruction received'
        }))

    async def handle_start_synchronizer(self, data):
        count = data.get('count', 0)
        for count_value in range(count, -1, -1):
            await self.send(text_data=json.dumps({
                'message': f'Game starts in {count_value}'
            }))

    async def handle_ongoing_synchronizer(self, data):
        current_multiplier = data.get('currentMultiplier', 0)
        # Use the currentMultiplier to render the ongoing graph
        # You can call the renderOngoingGraph function here or include the rendering logic directly
        await self.send(text_data=json.dumps({
            'message': f'Rendering ongoing graph for multiplier {current_multiplier}'
        }))
