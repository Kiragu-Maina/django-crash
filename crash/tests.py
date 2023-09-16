import json
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Load user data from the JSON file
with open('users.json', 'r') as json_file:
    users = json.load(json_file)

# Function to simulate user interaction
def simulate_user(user):
    phone_number = user['phone_number']
    password = user['password']

    # Initialize WebDriver for each user
    driver = webdriver.Chrome()
    
    try:
        # Navigate to your website
        driver.get('https://your-website.com')

        # Simulate user interactions (login, perform actions, etc.)
        # Example: Fill in login form and submit
        driver.find_element_by_id('phone_number_input').send_keys(phone_number)
        driver.find_element_by_id('password_input').send_keys(password)
        driver.find_element_by_id('login_button').click()

        # Perform other interactions as needed

    except Exception as e:
        print(f"Error for user {phone_number}: {str(e)}")
    finally:
        # Close the browser when done
        driver.quit()

# Number of concurrent users
num_users = 20

# Create a ThreadPoolExecutor to run concurrent sessions
with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
    # Start sessions for each user
    futures = [executor.submit(simulate_user, user) for user in users]

    # Wait for all sessions to complete
    concurrent.futures.wait(futures)

# All sessions are now complete
print("All sessions are complete.")
