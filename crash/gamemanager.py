import asyncio
import json
from .utils import ServerSeedGenerator
import time
from asyncio import Queue
import uuid
from .models import BettingWindow, CashoutWindow, Transactions, Games
from django.core.cache import cache
from channels.db import database_sync_to_async
import autobahn
import channels

class GameManager:
    game_manager_instance = None

    def __init__(self):
        self.crash_point = None
        self.hash_input = None
        self.generated_hash = None
        self.server_seed = None
        self.salt = None
         # Use asyncio.Queue for thread-safe management
        self.is_first_user = True
        self.current_multiplier = 0
        self.temp_consumers = [] 
        self.game_running = False
        self.game_ids = set()
        self.current_game_id = None
        self.usercancashout = False
        self.bettingcashoutmanager = BettingCashoutManager()
        self.game_lock = asyncio.Lock()
     
        


    @classmethod
    def get_instance(cls):
        if cls.game_manager_instance is None:
            print('gamemanager instance created')
            cls.game_manager_instance = cls()
        return cls.game_manager_instance

    async def add_consumer(self, consumer):
        
        
        print('add consumer called')
        
        self.temp_consumers.append(consumer)# Use put() for adding to the queue
        if self.is_first_user:
            print('self is first user')
            self.is_first_user = False
            if not self.game_running:
                print('game started')# Check if the game is not already running
                async with self.game_lock:
                    await self.run_game()
            
            
        else:
            await self.ongoing_game_state(consumer)



    async def remove_consumer(self, consumer):
        print('remove consumer called')
        try:
            self.temp_consumers.remove(consumer)
            await self.bettingcashoutmanager.remove_consumer(consumer)

            print(consumer, 'removed')
            if len(self.temp_consumers) == 0:
                self.is_first_user = True
                print('game should stop')
                await self.stop_game()
                
        except ValueError:
            print(consumer, 'not found in temp_consumers')
            return 

        # Remove the consumer from connected_consumers queue as well
        # This ensures that the queue doesn't hold a reference to removed consumers
     

    async def ongoing_game_state(self, consumer):
        if self.game_running:
            ongoing_state_data = {
                'type': 'ongoing_synchronizer',
                'currentMultiplier': self.current_multiplier,
                # ... (other relevant data)
            }
            print('ongoing called')
            await consumer.send(text_data=json.dumps(ongoing_state_data))
        else:
            # Handle the case where the game is not running
            await consumer.send(text_data=json.dumps({"type": "game_not_running"}))

       

    async def run_game(self):
        print('run_game called')
        self.game_running = True 
        game_id = await self.generate_unique_game_id()
        self.current_game_id = game_id
        print(f"Starting Game {game_id}")
        server_seed_generator = ServerSeedGenerator()
        self.generated_hash, self.server_seed, self.salt = server_seed_generator.get_generated_hash()
        self.crash_point = server_seed_generator.crash_point_from_hash()
        print(self.crash_point)
        if len(self.temp_consumers) == 0:
            print('game stopped')
            await self.stop_game()
            return
        for consumer in self.temp_consumers:
            print(consumer)
         

        
        print('15 seconds should start counting from here')
        await self.bettingcashoutmanager.allow_betting_period(game_id, self.generated_hash, self.server_seed, self.salt, self.temp_consumers)

        print('back after 15 seconds')
        await self.notify_users_game_start(game_id)
        await self.game_logic()
    async def notify_users_game_start(self, game_id):
        
        await self.send_instruction({"type": "start_synchronizer", "game_id": game_id})
            # Introduce a 1-second delay between messages


        




    async def game_logic(self):
        crash_point_seconds = int(self.crash_point)
        crash_point_milliseconds = int((self.crash_point - crash_point_seconds) * 1000)
        print(crash_point_seconds)
        print(crash_point_milliseconds)
        
        update_interval = 0.01  # Update interval in milliseconds
        count = 1
        await self.bettingcashoutmanager.open_cashout_window()
        while count <= self.crash_point:
           
            
            await asyncio.sleep(update_interval)  # Convert to seconds
            count += update_interval
            countofron = round(count, 2)
            self.current_multiplier = countofron
            
            # Send count data to consumers
            await self.send_instruction({"type": "count_update", "count": countofron})
        
        # Send crash instruction and print message
        await self.bettingcashoutmanager.close_cashout_window()
        await self.send_instruction({"type": "crash_instruction", "crash": self.crash_point})
        print(f"Crash occurred at {self.crash_point} seconds")

        # Wait for 5 seconds before running again
        self.game_running = False
        await asyncio.sleep(5)
        await self.run_game()

    async def stop_game(self):
        self.game_running = False
                      
    async def send_instruction(self, instruction):
        tasks = [self.safe_send_instruction(consumer, instruction) for consumer in self.temp_consumers]
        await asyncio.gather(*tasks)

    async def safe_send_instruction(self, consumer, instruction):
    
        try:
               
            await consumer.send(text_data=json.dumps(instruction))
        except autobahn.exception.Disconnected:
            print('exception')
            await consumer.disconnect()
            await consumer.close()
            raise channels.exceptions.StopConsumer


        
    async def generate_unique_game_id(self):
        # Generate a unique game ID using UUID
        while True:
            game_id = str(uuid.uuid4())
            if game_id not in self.game_ids:
                self.game_ids.add(game_id)
                return game_id
            
    async def handle_websocket_request(self, consumer, data):
        sent_game_id = data.get('game_id')
        sent_multiplier = data.get('multiplier')

        if sent_game_id == self.current_game_id:
            return True
        else:
            print("Received game ID doesn't match the current game.")
            return False
    
class BettingCashoutManager:
    def __init__(self):
        self.betting_window_key = 'betting_window_state'
        self.cashout_window_key = 'cashout_window_state'
        self.temp_consumers = [] 
        
     

    @database_sync_to_async
    def update_database_window(self, window_model, is_open):
        window, created = window_model.objects.get_or_create(id=1)
        window.is_open = is_open
        window.save()
        
    @database_sync_to_async
    def update_game_id(self, game_id, generated_hash, server_seed, salt):
        try:
            
            game_instance = Games(game_id=game_id, hash = generated_hash, server_seed = server_seed, salt = salt )
            game_instance.save()
            
            response_data = {
                'success': True,
                'message': 'game id updated',
                # You can include any relevant data in the response
            }
        except Exception as e:
            response_data = {
                
                'error': str(e)
            }
        print(response_data)
        

    async def set_window_state(self, window_model, is_open):
        await self.update_database_window(window_model, is_open)
        if window_model == BettingWindow:
            cache.set(self.betting_window_key, is_open, timeout=3600)
        else:
            cache.set(self.cashout_window_key, is_open, timeout=3600)

    async def allow_betting_period(self, game_id, generated_hash, server_seed, salt, temp_consumers):
        for consumer in temp_consumers:
            self.temp_consumers.append(consumer)
        
        await self.update_game_id(game_id, generated_hash, server_seed, salt)
        cache.set('game_id', game_id, timeout=3600)
        await self.set_window_state(BettingWindow, True)
        for count in range(15, 0, -1):
            await self.send_instruction({"type": "count_initial", "count": count })
            await asyncio.sleep(1)  # Allow betting for 15 seconds
        await self.set_window_state(BettingWindow, False)

    async def open_cashout_window(self):
        await self.set_window_state(CashoutWindow, True)
        

    async def close_cashout_window(self):
        await self.set_window_state(CashoutWindow, False)
    
    async def send_instruction(self, instruction):
        tasks = [self.safe_send_instruction(consumer, instruction) for consumer in self.temp_consumers]
        await asyncio.gather(*tasks)

    
    async def safe_send_instruction(self, consumer, instruction):
    
        try:
               
            await consumer.send(text_data=json.dumps(instruction))
        except autobahn.exception.Disconnected:
            print('exception')
            await consumer.disconnect()
            await consumer.close()
            raise channels.exceptions.StopConsumer

    async def remove_consumer(self, consumer):
        try:
            
            self.temp_consumers.remove(consumer)
            print(consumer, 'removed from betcashoutmanager')
        except ValueError:
            print(consumer, 'not found in temp_consumers')
            return