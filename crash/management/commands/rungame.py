import asyncio
from django.core.management.base import BaseCommand

import json
from ...utils import ServerSeedGenerator
import time

import uuid
from ...models import BettingWindow, CashoutWindow, Transactions, Games, GameSets
from django.core.cache import cache
from channels.db import database_sync_to_async
import autobahn
import channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import secrets

from django.db import transaction
import logging
logger = logging.getLogger(__name__)
logging.info('called gamemanager instance')
class Command(BaseCommand):
    help = 'Run the GameManager in the background'
    async def stop_games(self):
        # Get all running tasks in the current event loop
        running_tasks = asyncio.all_tasks()

        # Cancel all tasks except the current task (self)
        for task in running_tasks:
            if task is not asyncio.current_task():
                task.cancel()
            
       

    def handle(self, *args, **kwargs):
       
        asyncio.run(self.start_games())
        
    async def start_games(self):
        logging.info('start_game called')
        
        channel_names = ["group_1", "group_2", "group_3", "group_4"]
        
        game_manager_instances = [
            GameManager.get_instance(channel_name) for channel_name in channel_names
        ]
        
        
        while True:
            random_uuid = secrets.token_hex(4)  # 4 bytes = 8 characters

            # Set the 'unique_id' key in the cache with the generated random UUID
            cache.set('game_set_id', random_uuid)
            
            games = [game_manager_instance.start_game() for game_manager_instance in game_manager_instances]
            
            logging.info(f'Starting')
            
            # Await all tasks concurrently using asyncio.gather
            results = await asyncio.gather(*games, return_exceptions=True)
            
            for result in results:
                if result is True:
                    # Handle the case when a game returns True
                    pass
                else:
                    # Handle the case when a game returns False or raises an exception
                    pass

            # Add a delay (e.g., sleep for a while) before restarting tasks
            await asyncio.sleep(5)  # Adjust the duration as needed
        
      
       
    async def update_game_set(self):
        game_set_id = cache.get('game_set_id')

        @database_sync_to_async
        def save_game_set():
            with transaction.atomic():
                try:
                    gameset_instance = GameSets(game_set_id=game_set_id)
                    gameset_instance.save()
                except Exception as e:
                    logging.error("An error occurred:", str(e))

        await save_game_set()


            


class GameManager:
    game_manager_instances = {}

    def __init__(self, group_name):
        self.crash_point = None
        self.hash_input = None
        self.generated_hash = None
        self.server_seed = None
        self.salt = None
         # Use asyncio.Queue for thread-safe management
        self.is_first_user = True
        self.current_multiplier = 0
        self.game_running = False
        self.game_play = True
       
        self.game_ids = set()
        self.current_game_id = None
        self.usercancashout = False
        self.bettingcashoutmanager = BettingCashoutManager()
        self.game_lock = asyncio.Lock()
        self.group_name = group_name 
        self.game_set_id = None
        


    @classmethod
    def get_instance(cls, group_name):
        # Check if an instance for the given group_name already exists
        existing_instance = cls.game_manager_instances.get(group_name)
        

        if existing_instance is None:
            if len(cls.game_manager_instances) < 4:
                # If there are less than 4 instances, create a new one
                logging.info(f'{group_name}_gamemanager instance created')
                new_instance = cls(group_name)
                cls.game_manager_instances[group_name] = new_instance
                return new_instance
            else:
                # If there are already 4 instances, do not create a new one
                logging.error("Maximum number of instances reached (4).")
                return None
        else:
            # Return the existing instance for the given group_name
            return existing_instance

    async def stop_game(self):
        cache.delete(f"{self.game_set_id}_all_games_manager")
        self.game_play = False
        
    async def start_game(self):
        logging.info('start_game called')
        self.game_play = True
        await self.run_game()

       

    async def run_game(self):
        logging.info('run_game called')
        while self.game_play:
            
           
            self.game_running = True
            game_id = await self.generate_unique_game_id()
            self.current_game_id = game_id
            logging.info(f"Starting Game {game_id}")
            server_seed_generator = ServerSeedGenerator()
            self.generated_hash, self.server_seed, self.salt = server_seed_generator.get_generated_hash()
            self.crash_point = server_seed_generator.crash_point_from_hash()
            logging.info(self.crash_point)
           
             
    
            
            logging.info('15 seconds should start counting from here')
            await self.notify_users_game_start(game_id)
            
            self.game_play = await self.bettingcashoutmanager.allow_betting_period(self, self.group_name, game_id, self.generated_hash, self.server_seed, self.salt)
            
    
            logging.info('back after 15 seconds')
            if self.game_play == False:
                logging.info(self.game_play)
                break
           
            
            await self.game_logic()
    async def notify_users_game_start(self, game_id):
        logging.info('notify users called')
        data = {'type':'start_synchronizer','game_id':game_id, 'count':15}
        if self.group_name == 'group_1':
            channel_layer = get_channel_layer()
            
            await channel_layer.group_send(
                "realtime_group",  
                {
                    "type": "realtime.update",
                    "data": data,
                }
            )
            logging.info('sent', self.group_name)

        




    async def game_logic(self):
        crash_point_seconds = int(self.crash_point)
        crash_point_milliseconds = int((self.crash_point - crash_point_seconds) * 1000)
        logging.info(crash_point_seconds)
        logging.info(crash_point_milliseconds)
        
        update_interval = 0.01
        delay = 0.05# Update interval in milliseconds
        count = 1
        cache_key = f'{self.group_name}_game_multiplier'
        await self.bettingcashoutmanager.open_cashout_window(self.group_name)
        await self.send_instruction({"type": "count_update", "count": 'countofron'})
        # await asyncio.create_task(self.update_game_state_in_cache())
        # self.update_multiplier = asyncio.create_task(self.send_multiplier_every_five())
        
        
        while count <= self.crash_point:
           
            
            await asyncio.sleep(delay)  # Convert to seconds
            count += update_interval
            countofron = round(count, 2)
            self.current_multiplier = countofron
            
            
            cache.set(cache_key, countofron)
            
           
            
            
            
            # Send count data to consumers
           
        
        # Send crash instruction and logging.info message
        await self.bettingcashoutmanager.close_cashout_window()
        await self.send_instruction({"type": "crash_instruction", "crash": self.crash_point})
        channel_layer = get_channel_layer()
        logging.info(f"Crash for {self.group_name} occurred at {self.crash_point} seconds")
        
            
        cache.set(cache_key, 'Popped')
        data = {
            'group_name':self.group_name,
            'game_id':self.current_game_id,
        }
        await channel_layer.group_send(
                "realtime_group",  
                {
                    "type": "game.crashed",
                    "data":data,
                    
                }
            )
        

        # Wait for 5 seconds before running again
        await self.update_crashpoint_in_database(self.crash_point)
        
        await asyncio.sleep(5)
        
        
        self.game_running = False
        self.game_play = False
        
        
            
  
        
            
            
            
            
            
    @database_sync_to_async
    def update_crashpoint_in_database(self, crashpoint):
        try:
            with transaction.atomic():
                game = Games.objects.select_for_update().get(game_id=self.current_game_id)
                game.crash_point = crashpoint
                game.save()
            return True  # Indicate success
        except Games.DoesNotExist:
            return False  # Game does not exist

        

    async def update_game_state_in_cache(self):
       
        while self.game_running:
            
                # Update and cache the game state here
            cache.set(f'{self.group_name}_game_multiplier', self.current_multiplier, timeout=1)
            await asyncio.sleep(0.05)  # Adjust the update frequency as needed
        



    async def send_instruction(self, instruction):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"{self.group_name}",  # Use self.group_name
            {
                "type": "game.update",
                "data": instruction,
            }
        )


  


        
    async def generate_unique_game_id(self):
        # Generate a unique game ID using UUID
        while True:
            game_id = str(uuid.uuid4())
            if game_id not in self.game_ids:
                self.game_ids.add(game_id)
                return game_id
            
    async def handle_multiplier_validation(self, consumer, data):
        sent_game_id = data.get('game_id')
        sent_multiplier = data.get('multiplier')

        if (cache.get('cashout_window_state')):
            if sent_game_id == self.current_game_id:
                if sent_multiplier <= self.current_multiplier:
                    return True
        
        logging.info("Received game ID or multiplier or window closed doesn't match the current game.")
        return False
    
class BettingCashoutManager:
    def __init__(self):
        
        self.group_name = None
        self.betting_window_key = 'betting_window_state'
        self.cashout_window_key = f"{self.group_name}_cashout_window_state"
       
     

    @database_sync_to_async
    def update_database_window(self, window_model, is_open):
        window, created = window_model.objects.get_or_create(id=1)
        window.is_open = is_open
        window.save()
        
    @database_sync_to_async
    def update_game_id(self, game_id, generated_hash, server_seed, salt):
        
        
        try:
            
            game_instance = Games(group_name = self.group_name, game_id=game_id, hash = generated_hash, server_seed = server_seed, salt = salt )
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
        logging.info(response_data)
        

    async def set_window_state(self, window_model, is_open):
        await self.update_database_window(window_model, is_open)
        if window_model == BettingWindow:
            cache.set(self.betting_window_key, is_open, timeout=3600)
        else:
            cashout_window_key = f"{self.group_name}_cashout_window_state"
            
            cache.set(cashout_window_key, is_open, timeout=3600)

    async def allow_betting_period(self, gamemanager, group_name, game_id, generated_hash, server_seed, salt):
        
        self.group_name = group_name
       
        
        
        await self.update_game_id(game_id, generated_hash, server_seed, salt)
            
        
           
        
        cache.set(f'{group_name}_game_id', game_id, timeout=3600)
        
        await self.set_window_state(BettingWindow, True)
        
        for count in range(25, 0, -1):
            await self.send_instruction({"type": "count_initial", "count": count })
           
           
            
            await asyncio.sleep(1)  # Allow betting for 15 seconds
        await self.set_window_state(BettingWindow, False)
        return True

    async def open_cashout_window(self, group_name):
        logging.info('open cashout window called')
        
        self.group_name = group_name
        
        await self.set_window_state(CashoutWindow, True)
        

    async def close_cashout_window(self):
        await self.set_window_state(CashoutWindow, False)
    
    async def send_instruction(self, instruction):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
                f"{self.group_name}",
                {
                    "type": "game.update",
                    "data": instruction,
                }
            )

    

    
