import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer


import time

from .models import Clients, Transactions, Bank, Games
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import transaction
from decimal import Decimal
from django.core.cache import cache
from .gamemanager import GameManager

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
        cached_multiplier = cache.get('game_multiplier')
        if cached_multiplier is not None:
        # Send the cached_multiplier to the connected user
            await self.send(text_data=json.dumps({
                'type': 'ongoing_synchronizer',
                'cached_multiplier': cached_multiplier
            }))
        
   
    
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
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Remove this consumer from the GameManager instance
        # self.game_manager.remove_consumer(self)

    async def receive(self, text_data):
        try:
            print('receive called')
            print(text_data) 
            data = json.loads(text_data)
            message_type = data.get('type', '')
            print(data)
            
        
            if message_type == "crash_instruction":
                await self.handle_crash_instruction(data)
            elif message_type == "start_synchronizer":
                await self.handle_start_synchronizer(data)
            elif message_type == "cashout_validate":
                response = await self.handle_multiplier_validation(data)
                if response:
                    await self.update_cashout(data)
                    
            
        except Exception as e:
            print(f"Error in receive: {str(e)}")
    async def handle_multiplier_validation(self, data):
        sent_game_id = data.get('game_id')
        sent_multiplier = data.get('multiplier')
        cached_multiplier = cache.get('game_multiplier')
        print('cached_multiplier', cached_multiplier)

        if (cache.get('cashout_window_state')):
            
                if sent_multiplier <= cached_multiplier:
                    return True
        
        print("Received game ID or multiplier or window closed doesn't match the current game.")
        return False

    @database_sync_to_async
    def update_cashout(self, data):
        with transaction.atomic():
            user=self.scope["user"]
        
            try:
                new_transaction = Transactions.objects.filter(user=user).order_by('created_at').last()
                games_game_id = Games.objects.order_by('created_at').last()

                if data.get('game_id') == new_transaction.game_id == games_game_id.game_id:
                    if not new_transaction.game_played:
                        new_transaction.multiplier = data.get('multiplier')
                        new_transaction.won = new_transaction.bet * float(data.get('multiplier'))
                        new_transaction.game_played = True
                        new_transaction.save()

                        try:
                            bank_instance = Bank.objects.select_for_update().get(user=user)
                            bank_instance.balance += Decimal(new_transaction.won)
                            bank_instance.save()
                        except Bank.DoesNotExist:
                            response_data = {'type':'cashout', 'status': 'error', 'message': 'no_bank'}

                        response_data = {
                            'type':'cashout',
                            'status': 'success',
                            'message': 'Cashout successful'
                        }
                    else:
                        response_data = {
                            'type':'cashout',
                            'status': 'error',
                            'message': 'User already cashed out'
                        }
                else:
                    response_data = {
                        'type':'cashout',
                        'status': 'error',
                        'message': 'Non-matching game_id'
                    }

            except Exception as e:
                response_data = {
                    'type':'cashout',
                    'status': 'error',
                    'message': 'Cashout failed',
                    'error': str(e)
    
                  }
                
            client = Clients.objects.filter(user=user).first()
        channel_name = client.channel_name
        print(channel_name)
        
        

        # Send the update to the user's channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            f"{channel_name}",  # Use a unique channel name per user
            {
                "type": "balance.update",
                "data": response_data,
                
            }
        )
    async def start_game(self, event):
        print('start_game called')
        self.game_play = asyncio.create_task(self.game_manager.start_game()) 
        # self.send(text_data=json.dumps(response_data))
    async def stop_game(self, event):
        print('stop_game called')
        await self.game_manager.stop_game() 
    async def game_update(self, event):
        print('game update')
        updated_item = event['data']
        await self.send(text_data=json.dumps(updated_item))
    
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
        with transaction.atomic():
            client, created = Clients.objects.get_or_create(user=user)
            client.channel_name = channel_name
            client.save()
            return client


    @database_sync_to_async
    def delete_client(self, user):
        with transaction.atomic():
            Clients.objects.filter(user=user).delete()

    async def receive(self, text_data):
        # Handle received data
        pass

    async def balance_update(self, event):
        # Handles the "balance.update" event when it's sent to us.
        print('balance update')
        updated_item = event['data']
        await self.send(text_data=json.dumps(updated_item))

