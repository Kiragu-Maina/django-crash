import asyncio
import json
import logging
import httpx
from websockets import connect, WebSocketException

import re  # For regular expressions




class Command(BaseCommand):
    help = 'Respawn game in the background'

   

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        asyncio.run(self.main())

    
        
            
        
    async def login(self):
        try:
            logging.info("Logging in...")
            async with httpx.AsyncClient() as client:
                response = await client.post('https://django-crash-production.up.railway.app/login/', data={
                    'username': '0714313598',
                    'password': 'admin',
                }, timeout=30)

                if response.status_code == 200:
                    logging.info("Login successful")

                    # Extract the CSRF token from the response cookies or headers
                    csrf_token = None
                    
                    # Check if the token is present in cookies
                    if 'csrftoken' in response.cookies:
                        csrf_token = response.cookies['csrftoken']

                    # If not found in cookies, check response headers
                    if not csrf_token:
                        csrf_match = re.search(r"csrftoken=([\w\d]+);", response.headers.get("set-cookie", ""))
                        if csrf_match:
                            csrf_token = csrf_match.group(1)

                    if csrf_token:
                        logging.info(f"CSRF token: {csrf_token}")
                        return response.cookies, csrf_token
                    else:
                        logging.error("CSRF token not found")
                        return None, None
                else:
                    logging.error("Login failed")
                    return None, None
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            return None, None


    async def main(self):
        session, csrf_token = await self.login()
        
        if session:
            async with connect('wss://django-crash-production.up.railway.app/ws/realtime/') as ws_client:
                logging.info("WebSocket connection established.")
            
                while True:
                    try:
                        # Wait for incoming WebSocket messages
                        message = await ws_client.recv()
                        logging.info("Received message: %s", message)
                        message_data = json.loads(message)
                        message_type = message_data.get('type')
            
                        if message_type == "start_synchronizer":
                            # Listen for a "mid_start_synchronizer" message with a timeout of 5 seconds
                            mid_message = await asyncio.wait_for(ws_client.recv(), timeout=5)
                            logging.info("Received mid_start_synchronizer message: %s", mid_message)
            
                        else:
                            # Handle other message types if needed
                            pass
            
                    except WebSocketException as e:
                        logging.error("WebSocket error: %s", str(e))
                    except asyncio.TimeoutError:
                        # Handle timeout for mid_start_synchronizer message
                        logging.warning("mid_start_synchronizer message not received within 5 seconds. Sending a POST request...")
                        async with httpx.AsyncClient() as client:
                            response = await client.post('https://django-crash-production.up.railway.app/adminpage/', 
                                                        data={'action': 'start', 'csrfmiddlewaretoken': f'{csrf_token}'}, 
                                                        cookies=session,
                                                        timeout=30)
                            logging.info("POST response: %s", response.text)