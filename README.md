# django-crash
A reimagined version of the popular Aviator game, featuring four concurrent game sessions. In this game, players can choose from four balloons and place bets on which balloon they believe will pop last. The project involved designing an engaging user interface, implementing real-time game mechanics, and ensuring a seamless betting experience.

## Features

- **Four Concurrent Games**: Players can choose among four balloons and place a bet for preemptive cashout in four simultaneous game sessions.
- **Betting System**: Added functionality for players to place bets on the balloon they think will pop last.
- **Real-time Mechanics**: Ensured smooth and real-time game interactions using WebSockets.
- **Engaging UI**: Designed an intuitive and attractive user interface to enhance user experience.

## Technologies Used

- **Backend**: Django, Celery, Celery Beat, Postgres, Redis, asyncio, hmac, hashlib, and more Python packages.
- **Frontend**: HTML, CSS, JavaScript, PhaserJS
- **Real-time Communication**: WebSockets using Django Channels

## How to Run the Application

1. Create a virtual environment:
    ```bash
    python -m venv env
    ```

2. Activate the virtual environment:
    ```bash
    source env/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Django development server:
    ```bash
    python manage.py runserver
    ```

5. Start the Celery worker:
    ```bash
    celery -A crashsite worker --loglevel=info
    ```

6. Start the Celery beat scheduler:
    ```bash
    celery -A crashsite beat --loglevel=info
    ```

Then, go to `127.0.0.1:8000` for the user page and `127.0.0.1:8000/adminpage` for the admin page. On the admin page, press "Start Game" to start the game.
