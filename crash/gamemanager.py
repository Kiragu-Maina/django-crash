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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



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
        
        


    @classmethod
    def get_instance(cls, group_name):
        # Check if an instance for the given group_name already exists
        existing_instance = cls.game_manager_instances.get(group_name)

        if existing_instance is None:
            if len(cls.game_manager_instances) < 4:
                # If there are less than 4 instances, create a new one
                print(f'{group_name}_gamemanager instance created')
                new_instance = cls(group_name)
                cls.game_manager_instances[group_name] = new_instance
                return new_instance
            else:
                # If there are already 4 instances, do not create a new one
                print("Maximum number of instances reached (4).")
                return None
        else:
            # Return the existing instance for the given group_name
            return existing_instance

    async def stop_game(self):
        self.game_play = False
        
    async def start_game(self):
        print('start_game called')
        self.game_play = True
        await self.run_game()

       

    async def run_game(self):
        print('run_game called')
        while self.game_play:
            
           
            self.game_running = True
            game_id = await self.generate_unique_game_id()
            self.current_game_id = game_id
            print(f"Starting Game {game_id}")
            server_seed_generator = ServerSeedGenerator()
            self.generated_hash, self.server_seed, self.salt = server_seed_generator.get_generated_hash()
            self.crash_point = server_seed_generator.crash_point_from_hash()
            print(self.crash_point)
           
             
    
            
            print('15 seconds should start counting from here')
            await self.notify_users_game_start(game_id)
            
            await self.bettingcashoutmanager.allow_betting_period(self.group_name, game_id, self.generated_hash, self.server_seed, self.salt)
            
    
            print('back after 15 seconds')
           
            self.game_multiplier = asyncio.create_task(self.update_game_state_in_cache())
            await self.game_logic()
    async def notify_users_game_start(self, game_id):
        print('notify users called')
        data = {'type':'start_synchronizer','game_id':game_id, 'count':15}
        
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            "realtime_group",  
            {
                "type": "realtime.update",
                "data": data,
            }
        )
        print('sent')

        




    async def game_logic(self):
        crash_point_seconds = int(self.crash_point)
        crash_point_milliseconds = int((self.crash_point - crash_point_seconds) * 1000)
        print(crash_point_seconds)
        print(crash_point_milliseconds)
        
        update_interval = 0.01
        delay = 0.05# Update interval in milliseconds
        count = 1
        await self.bettingcashoutmanager.open_cashout_window(self.group_name)
        await self.send_instruction({"type": "count_update", "count": 'countofron'})
        # self.update_multiplier = asyncio.create_task(self.send_multiplier_every_five())
        
        
        while count <= self.crash_point:
           
            
            await asyncio.sleep(delay)  # Convert to seconds
            count += update_interval
            countofron = round(count, 2)
            self.current_multiplier = countofron
            all_games_manager = cache.get('all_games_manager')
            if all_games_manager == 5:
                self.game_running = False
                self.game_play = False
                return
            
            
            
            
            # Send count data to consumers
           
        
        # Send crash instruction and print message
        await self.bettingcashoutmanager.close_cashout_window()
        await self.send_instruction({"type": "crash_instruction", "crash": self.crash_point})
        print(f"Crash for {self.group_name} occurred at {self.crash_point} seconds")

        # Wait for 5 seconds before running again
        
        await asyncio.sleep(5)
        all_games_manager = cache.get('all_games_manager')
        if all_games_manager is None:
            all_games_manager = 0
    
        all_games_manager = int(all_games_manager) + 1
    
        cache.set('all_games_manager', all_games_manager)
        self.game_running = False
        self.game_play = False
        
        if all_games_manager == 4:
            print('multiplier', all_games_manager)
            cache.set('all_games_manager', 0)
            channel_layer = get_channel_layer()
        
            await channel_layer.group_send(
                "realtime_group",  
                {
                    "type": "restart.game",
                    
                }
            )
        elif all_games_manager == 5:
            return
            
            
            
            
            
       
        

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
        
        print("Received game ID or multiplier or window closed doesn't match the current game.")
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
        print(response_data)
        

    async def set_window_state(self, window_model, is_open):
        await self.update_database_window(window_model, is_open)
        if window_model == BettingWindow:
            cache.set(self.betting_window_key, is_open, timeout=3600)
        else:
            cashout_window_key = f"{self.group_name}_cashout_window_state"
            
            cache.set(cashout_window_key, is_open, timeout=3600)

    async def allow_betting_period(self, group_name, game_id, generated_hash, server_seed, salt):
        
        self.group_name = group_name
       
        
        
        await self.update_game_id(game_id, generated_hash, server_seed, salt)
            
        
           
        
        cache.set(f'{group_name}_game_id', game_id, timeout=3600)
        
        await self.set_window_state(BettingWindow, True)
        
        for count in range(30, 0, -1):
            await self.send_instruction({"type": "count_initial", "count": count })
            
            await asyncio.sleep(1)  # Allow betting for 15 seconds
        await self.set_window_state(BettingWindow, False)

    async def open_cashout_window(self, group_name):
        print('open cashout window called')
        
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

    
