import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import random
import asyncio

# Load user data from the JSON file
with open('users.json', 'r') as json_file:
    users = json.load(json_file)

# Function to simulate user interaction
async def simulate_user(user):
    print('simulate_user called')
    phone_number = user['phone_number']
    password = user['password']

     # Set up ChromeOptions for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode

    # Initialize WebDriver for each user with headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    
    
    try:
        # Navigate to your website
        driver.get('https://ee61-102-68-79-97.ngrok.io')
        time.sleep(5)


        # Navigate to the web page where the "Sign In" link is located
       

        # Locate and click on the "Sign In" link
        try:
            sign_in_link = driver.find_element_by_link_text('Sign In')  # Using the link text to locate the element
            sign_in_link.click()
            print("Clicked on 'Sign In' link.")
            try: 
                driver.find_element_by_id('phone_number1').send_keys(phone_number)
                driver.find_element_by_id('password').send_keys(password)
                driver.find_element_by_id('login_submit_btn').click()

                # Perform other interactions as needed
                async with websockets.connect('wss:/ee61-102-68-79-97.ngrok.io/ws/realtime/') as websocket:
                    
                        

                    # Receive a message
                    response_json = await websocket.recv()
                    response_data = json.loads(response_json)

                    if response_data['type'] == "start_synchronizer":
                        bet_amount = random.randint(1, 3000)
                        driver.find_element_by_id('selected-amount').send_keys(str(bet_amount))  # Convert to string
                        driver.find_element_by_id('bet-button').click()
                        print("Clicked on 'BET'.")
                                
                
                

            except Exception as e:
                print(f"Error for user {phone_number}: {str(e)}")
            
        except Exception as e:
            print("Error:", str(e))



        driver.find_element_by_id('phone_number_input').send_keys(phone_number)
        driver.find_element_by_id('password_input').send_keys(password)
        driver.find_element_by_id('login_button').click()

        # Perform other interactions as needed

    except Exception as e:
        print(f"Error for user {phone_number}: {str(e)}")
    finally:
        # Close the browser when done
        driver.quit()

num_users = 5
print('starting loop')
# Create an event loop for asyncio
loop = asyncio.get_event_loop()

# Create a list of tasks to run concurrently
tasks = [simulate_user(user) for user in users]

# Run the tasks concurrently
loop.run_until_complete(asyncio.gather(*tasks))

# All sessions are now complete
print("All sessions are complete.")