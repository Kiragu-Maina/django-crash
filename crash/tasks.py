from celery import shared_task
from .gamemanager import GameManager
import asyncio
from django.core.cache import cache
from celery.exceptions import Terminated
from crashsite.celery import app
import time
import secrets
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task
def send_updates():
    print('sending all game updates')
  
    data = {
        'type': 'all_games_updates'
    }
    group_game_multipliers = {
        'group_1': 'group_1_game_multiplier',
        'group_2': 'group_2_game_multiplier',
        'group_3': 'group_3_game_multiplier',
        'group_4': 'group_4_game_multiplier',
    }
    all_groups_wait_for_new_game = 0
    
    for group, cache_key in group_game_multipliers.items():
        cached_multiplier = cache.get(cache_key)
       
            
        if cached_multiplier == 'Popped':
            data[group] = cached_multiplier
            all_groups_wait_for_new_game += 1
            cache.set(cache_key, 'Wait for new game')
        elif cached_multiplier == 'Wait for new game':
            data[group] = cached_multiplier
            
            all_groups_wait_for_new_game += 1
        elif cached_multiplier is None:
            all_groups_wait_for_new_game += 1
        else:
            data[group] = cached_multiplier
            
            
    if all_groups_wait_for_new_game == 4:
        num = cache.get('new_game_in')
        if num == False:
            return
        if num == 0:
            num = 6 
        if num is not None:        
            num -= 1
        
        for group, cache_key in group_game_multipliers.items():            
            
            data[group] = f'New game in {num}s'
        if num == 1:
            send_to_channel(data)
            cache.set('new_game_in', False)
            
            return

        cache.set('new_game_in', num)
        
        
    else:
        cache.set('new_game_in', 0)
        pass
    
    send_to_channel(data)
    
    
    
def send_to_channel(data):
            
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "table_updates",
        {
            "type": "table.update",
            "data": data,
        }
    )
    return True


@shared_task
def start_game():
    
    
    def start_games():
        return True
        

    start_games()

@shared_task
def stop_game():
    

    def stop_games():
        
        
      return True

    stop_games()

@shared_task
def data_to_admin():
    data = {
            'type':'player_update',
        'players_online':cache.get("realtime_group_user_count"),
        'players_betting':cache.get("realtime_betting_users_count"),
        'players_won':cache.get("bets_won_user_count"),
        'players_lost':cache.get("bets_lost_user_count"),
    }
    
  
        # Send the update using Channels' channel layer
    channel_layer = get_channel_layer()
       
    async_to_sync(channel_layer.group_send)(
            "admin_updates",
            {
                "type": "pot.update",
                "data": data,
            }
        )
    return True