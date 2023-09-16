from celery import shared_task
from .gamemanager import GameManager
import asyncio
from django.core.cache import cache
from celery.exceptions import Terminated
from crashsite.celery import app

channel_name_1 = "group_1"
channel_name_2 = "group_2"
channel_name_3 = "group_3"
channel_name_4 = "group_4"

game_manager_instances = [
    GameManager.get_instance(channel_name_1),
    GameManager.get_instance(channel_name_2),
    GameManager.get_instance(channel_name_3),
    GameManager.get_instance(channel_name_4),
]

@shared_task
def start_game():
    print('start_game called')
    
    def start_games():
        cache.set('all_games_manager', 0)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asyncio.gather(*[game_manager_instance.start_game() for game_manager_instance in game_manager_instances]))
        finally:
            loop.close()

    start_games()

@shared_task
def stop_game():
    print('stop_game called')

    def stop_games():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asyncio.gather(*[game_manager_instance.stop_game() for game_manager_instance in game_manager_instances]))
        finally:
            loop.close()
        # Replace with your worker name
        try:
            app.control.purge()
        except Terminated:
            pass  # Worker alr

    stop_games()
