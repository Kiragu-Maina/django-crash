import asyncio
import json
import logging
import httpx
from websockets import connect, WebSocketException
from django.core.management.base import BaseCommand

import re  # For regular expressions




class Command(BaseCommand):
    help = 'Respawn game in the background'

   

    def handle(self, *args, **options):
        logging.basicConfig(level=print)
        asyncio.run(self.main())

    
        
            
        
    async def login(self):
        try:
            print("Logging in...")
            async with httpx.AsyncClient() as client:
                response = await client.post('https://django-crash-production.up.railway.app/login/', data={
                    'username': '0714313598',
                    'password': 'admin',
                }, timeout=30)

                if response.status_code == 200:
                    print("Login successful")

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
                        print(f"CSRF token: {csrf_token}")
                        return response.cookies, csrf_token
                    else:
                        print("CSRF token not found")
                        return None, None
                else:
                    print("Login failed")
                    return None, None
        except Exception as e:
            print(f"Login error: {str(e)}")
            return None, None


    async def main(self):
        print('main called')
        while True:
            session, csrf_token = await self.login()
            
            if session:
                async with connect('wss://django-crash-production.up.railway.app/ws/realtime/') as ws_client:
                    print("WebSocket connection established.")
                
                    while True:
                        try:
                            # Wait for incoming WebSocket messages
                            message = await ws_client.recv()
                            print("Received message: %s", message)
                            message_data = json.loads(message)
                            message_type = message_data.get('type')
                
                            if message_type == "start_synchronizer":
                                # Listen for a "mid_start_synchronizer" message with a timeout of 5 seconds
                                mid_message = await asyncio.wait_for(ws_client.recv(), timeout=5)
                                print("Received mid_start_synchronizer message: %s", mid_message)
                
                            else:
                                # Handle other message types if needed
                                pass
                
                        except WebSocketException as e:
                        
                            print(f"WebSocket error: {str(e)}. Attempting to reconnect")
            
                            # Add a delay before attempting to reconnect (e.g., 5 seconds)
                            await asyncio.sleep(2)
                            break
                        except asyncio.TimeoutError:
                            # Handle timeout for mid_start_synchronizer message
                            print("mid_start_synchronizer message not received within 5 seconds. Sending a POST request...")
                            async with httpx.AsyncClient() as client:
                                response = await client.post('https://django-crash-production.up.railway.app/adminpage/', 
                                                            data={'action': 'start', 'csrfmiddlewaretoken': f'{csrf_token}'}, 
                                                            cookies=session,
                                                            timeout=30)
                                print("POST response: %s", response.text)