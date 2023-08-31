import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from .gamemanager import GameManager

import time

from .models import Clients
from channels.db import database_sync_to_async

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            pass
        else:
            
            self.username = self.scope["user"].user_name        
            print(f"User {self.username} connected to game room")
        
        self.room_group_name = 'realtime_group'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        self.game_manager = GameManager.get_instance()
        
        # Start the heartbeat mechanism
         # Start the heartbeat mechanism as a concurrent task
        # self.heartbeat_task = asyncio.create_task(self.heartbeat())
        self.game_play = asyncio.create_task(self.game_manager.add_consumer(self))
    
    async def heartbeat(self):
        print('heartbeat called')
        while True:
            response_received = asyncio.Event()

            async def wait_for_response():
                try:
                    while not response_received.is_set():
                        await self.receive_json()
                        response_received.set()  # Set the event when response is received
                except asyncio.TimeoutError:
                    pass

            response_task = asyncio.create_task(wait_for_response())

            await asyncio.sleep(5)  # Wait for 5 seconds
            await self.send(text_data=json.dumps({'type': 'heartbeat'}))
            print('heartbeat sent')

            try:
                await asyncio.wait_for(response_received.wait(), timeout=5)
                print('Response received within timeout')
            except asyncio.TimeoutError:
                print('Response not received within timeout. Initiating disconnect...')
                # await self.disconnect('server_initiated')

            response_task.cancel()  # Clean up the response handling task
            print('Response handler task canceled')

        

    async def disconnect(self, close_code):
        # Leave room group
        # Remove this consumer from the GameManager instance
        print('disconnect called and remove consumer from game called')
        await self.game_manager.remove_consumer(self)
        print('game_manager called to remove')

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove this consumer from the GameManager instance
        self.game_manager.remove_consumer(self)

    async def receive(self, text_data):
        try:
            print('receive called')
            data = json.loads(text_data)
            message_type = data.get('type', '')
            print(data)
            
        
            if message_type == "crash_instruction":
                await self.handle_crash_instruction(data)
            elif message_type == "start_synchronizer":
                await self.handle_start_synchronizer(data)
            elif message_type == "ongoing_synchronizer":
                await self.handle_ongoing_synchronizer(data)
            
        except Exception as e:
            print(f"Error in receive: {str(e)}")


    
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
   

class TableUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.group_name = "table_updates"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def table_update(self, event):
        print('table update')
        updated_item = event['data']
        await self.send(text_data=json.dumps(updated_item))

    async def update_table(self, data):
        print('update_data called')
        await self.channel_layer.group_send(self.group_name, {
            "type": "table.update",
            "data": data,
        })

    async def receive(self, text_data):
        # Do nothing with received data
        pass
    
    
class BalanceUpdateConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()
        await self.assign_channel_to_user()

    async def disconnect(self, close_code):
        await self.delete_channel_for_user()

    async def assign_channel_to_user(self):
        user = self.scope["user"]
        if user.is_authenticated:
            print('user is authenticated')
            client = await self.update_client(user, self.channel_name)
            print('channel_name:', client.channel_name)

    async def delete_channel_for_user(self):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.delete_client(user)

    @database_sync_to_async
    def update_client(self, user, channel_name):
        client = Clients.objects.select_for_update().get(user=user)
        
        client.channel_name = channel_name
        client.save()
        return client

    @database_sync_to_async
    def delete_client(self, user):
        Clients.objects.filter(user=user).delete()

    async def receive(self, text_data):
        # Handle received data
        pass

    async def balance_update(self, event):
        # Handles the "balance.update" event when it's sent to us.
        print('balance update')
        updated_item = event['data']
        await self.send(text_data=json.dumps(updated_item))