import asyncio
import json
from .utils import ServerSeedGenerator
import time
from asyncio import Queue

class GameManager:
    game_manager_instance = None

    def __init__(self):
        self.crash_point = None
        self.connected_consumers = Queue()  # Use asyncio.Queue for thread-safe management
        self.is_first_user = True
        self.current_multiplier = 0
        self.temp_consumers = [] 
        self.game_running = False


    @classmethod
    def get_instance(cls):
        if cls.game_manager_instance is None:
            cls.game_manager_instance = cls()
        return cls.game_manager_instance

    async def add_consumer(self, consumer):
        print('add consumer called')
        await self.connected_consumers.put(consumer)
        self.temp_consumers.append(consumer)# Use put() for adding to the queue
        if self.is_first_user:
            print('self is first user')
            self.is_first_user = False
            await self.run_game()
            
        else:
            await self.ongoing_game_state(consumer)



    async def remove_consumer(self, consumer):
        try:
            self.temp_consumers.remove(consumer)
        except ValueError:
            pass

        # Remove the consumer from connected_consumers queue as well
        # This ensures that the queue doesn't hold a reference to removed consumers
        while True:
            queued_consumer = await self.connected_consumers.get()
            if queued_consumer is None or queued_consumer == consumer:
                break
            await self.connected_consumers.put(queued_consumer)

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
        server_seed_generator = ServerSeedGenerator()
        generated_hash = server_seed_generator.generate_hash()
        self.crash_point = server_seed_generator.crash_point_from_hash()
        print(self.crash_point)
         

       
        for consumer in self.temp_consumers:
            print('in run game',consumer)
            await consumer.send(text_data=json.dumps({"type": "start_synchronizer", "count": '5'}))
        

        await asyncio.sleep(6)

        await self.game_logic()

    async def game_logic(self):
        crash_point_seconds = int(self.crash_point)
        crash_point_milliseconds = int((self.crash_point - crash_point_seconds) * 1000)
        print(crash_point_seconds)
        print(crash_point_milliseconds)
        
        update_interval = 0.01  # Update interval in milliseconds
        count = 1
        
        while count <= self.crash_point:
            await asyncio.sleep(update_interval)  # Convert to seconds
            count += update_interval
            countofron = round(count, 2)
            self.current_multiplier = countofron
            
            # Send count data to consumers
            await self.send_instruction({"type": "count_update", "count": countofron})
        
        # Send crash instruction and print message
        await self.send_instruction({"type": "crash_instruction", "crash": self.crash_point})
        print(f"Crash occurred at {self.crash_point} seconds")

        # Wait for 5 seconds before running again
        self.game_running = False
        await asyncio.sleep(5)
        await self.run_game()


                      
    async def send_instruction(self, instruction):
        tasks = [self.safe_send_instruction(consumer, instruction) for consumer in self.temp_consumers]
        await asyncio.gather(*tasks)

    async def safe_send_instruction(self, consumer, instruction):
        try:
            await consumer.send(text_data=json.dumps(instruction))
        except Exception as e:
            print(f"Error sending instruction to consumer: {e}")
          