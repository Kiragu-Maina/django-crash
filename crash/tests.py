import random
import json
import asyncio
import logging
import httpx
import websockets
import time
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

class WebSocketClient:
    def __init__(self, host):
        self.host = host
        self.ws = None

    async def connect(self):
        logging.info('Connecting to WebSocket...')
        self.ws = await websockets.connect(self.host, compression=None, origin="https://django-crash-testing.up.railway.app")

    async def send_message(self, message):
        await self.ws.send(json.dumps(message))
        

    async def receive_message(self):
        return await self.ws.recv()

    async def disconnect(self):
        logging.info('Disconnecting WebSocket...')
        await self.ws.close()

class UserSimulator:
    def __init__(self, user):
        self.user = user
        self.phone_number = user['phone_number']
        self.password = user['password']
        self.user_name = user['user_name']
        self.host = "https://django-crash-testing.up.railway.app"
        self.session = None
        self.ws_client = None
        self.ws_client2 = None
        
     
        
        self.wait_time = random.randint(5, 15)  # Add a random wait time between tasks
       
        self.allow_betting = True
        self.time_to_play = 10
        self.crashed = False
        self.cashout_event = asyncio.Event()

        
        

    async def login(self):
        logging.info(f"Logging in as {self.phone_number}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{self.host}/login/', data={
                'username': self.phone_number,
                'password': self.password,
            }, timeout=30)

            if response.status_code == 200:
                logging.info("Login successful")
                self.session = response.cookies
                logging.info(response)
                return True
            else:               
                logging.error("Login failed")
                return False
            

    async def simulate_user(self, game_id):            

        bet_amount = random.randint(1, 3000)
        bet_amount_str = str(bet_amount)
        balloon_chosen = random.randint(1, 4)
        selected_amount_input = bet_amount_str
        group_name = f"group_{balloon_chosen}"
        

        async def place_bet():
            start_time = time.time()  # Get the current time
    
            while time.time() - start_time <= 15:  # Retry within a 10-second window
                time_to_wait = round(random.uniform(0.1, 2), 2)
                await asyncio.sleep(time_to_wait)
                async with httpx.AsyncClient(cookies=self.session) as client:
                    response = await client.post(
                        f'{self.host}/placebet/',
                        data={'bet_amount': selected_amount_input, 'group_name': group_name},
                        timeout=30
                    )

                    if response.status_code == 200:
                        logging.info("Bet placement successful")
                        logging.info("Clicked on 'BET'")
                        
                        break  # Break out of the retry loop on success
                    else:
                        time_to_wait = round(random.uniform(0.1, 2), 2)
                        await asyncio.sleep(time_to_wait)
                        logging.warning(f"Bet placement failed. Retrying in {time_to_wait} second(s)...")
                        
            else:
                logging.warning("Exceeded the 5-second time window. Aborting bet placement.")
                return
            

        await place_bet()
        
        await self.bet_placing_and_cashout(group_name, game_id)
        

        

    async def bet_placing_and_cashout(self, group_name, game_id):
        self.ws_client2 = WebSocketClient(f'wss://django-crash-testing.up.railway.app/ws/real_time_updates/{group_name}/')
       
        await self.ws_client2.connect()

        try:
            while True:
                self.crashed = False
                message = await self.ws_client2.receive_message()
                logging.info(message)
                message_data = json.loads(message)
                message_type = message_data.get('type')

                if message_type == "crash_instruction":
                    self.crashed = True
                    self.cashout_event.set()
                    logging.info("Heard 'crash_instruction'")
                    await self.ws_client2.disconnect()
                    return
                    
                    
                    
                elif message_type == "count_update":
                    
                    await self.cashout(group_name, game_id)
                    
                    return
                    
                
                    
        finally:
            await self.ws_client2.disconnect()
           
    async def cashout(self, group_name, game_id):
            time_to_wait = round(random.uniform(1, 20), 2)
            self.time_to_play = time_to_wait
            update_interval = 0.01
            delay = 0.05
            count = 1
            logging.info(f"Waiting for {time_to_wait} seconds...")

            try:
                while count <= time_to_wait:
                    # Check for cancellation request
                    if self.cashout_event.is_set():
                        logging.info("Cashout operation canceled.")
                        return

                    await asyncio.sleep(delay)
                    if not self.crashed:
                        count += update_interval
                    else:
                        logging.info('Game crashed')
                        break

                # Signal that the cashout operation is ready to proceed
                self.cashout_event.set()
                await asyncio.sleep(5)
                logging.info("Sending 'cashout_validate' message")
                message = {'type': 'cashout_validate', 'multiplier': time_to_wait, 'game_id': game_id, 'user_name': self.user_name, 'password': 'qwertyadu'}
                await self.ws_client2.send_message(message)
            except asyncio.CancelledError:
                logging.info("Cashout operation canceled.")
                raise  # Re-raise the CancelledError if needed


        
    
async def login_users(selected_users):
    user_simulators = [UserSimulator(user) for user in selected_users]
    logins = [user_simulator.login() for user_simulator in user_simulators]
    await asyncio.gather(*logins)  # Gather and await both user_simulators and logins concurrently
    return user_simulators

async def run_simulations(user_simulators, game_id):
    tasks = [user_simulator.simulate_user(game_id) for user_simulator in user_simulators]
    await asyncio.gather(*tasks)
    

# Function to simulate user
def simulate_user(user_simulator, game_id):
    asyncio.run(user_simulator.simulate_user(game_id))

async def main():
    with open('users-prod.json', 'r') as json_file:
        users = json.load(json_file)

    num_users = 5
    selected_users = random.sample(users, num_users)

    # Create and login users concurrently
    user_simulators = await login_users(selected_users)

    # Create a WebSocket client
    ws_client = WebSocketClient('wss://django-crash-testing.up.railway.app/ws/realtime/')
    await ws_client.connect()

    while True:
        message = await ws_client.receive_message()
        logging.info(message)
        message_data = json.loads(message)
        message_type = message_data.get('type')
        
        active_processes = []

        if message_type == "start_synchronizer":
            # Terminate any active processes
            for process in active_processes:
                if process.is_alive():
                    process.terminate()
                    process.join()
            active_processes.clear()

            # Start new processes
            for user_simulator in user_simulators:
                process = multiprocessing.Process(target=simulate_user, args=(user_simulator, message_data.get('game_id')))
                active_processes.append(process)
                process.start()

        else:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.info(str(e))