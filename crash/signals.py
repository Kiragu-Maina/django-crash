from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Transactions, User, Bank, Clients, Games, OwnersBank, GameSets

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal
from .tasks import start_game, stop_game
import time


@receiver(post_save, sender=Transactions)
def transaction_saved(sender, instance, **kwargs):
    # Construct the data that you want to send to the WebSocket consumer
    print('signals called')
    if instance.game_played == True:
        if instance.won > 0:
            data_type ="table_update"
            
        elif instance.won == 0:
            data_type ="lose_update"
        else:
            data_type ="lose_update"
    else:
        data_type = "bet_placed_update"
        
    if str(instance.group_name) == 'group_1':
        balloon = 'blue'
    elif str(instance.group_name) == 'group_2':
        balloon = 'red'
    elif str(instance.group_name) == 'group_3':
        balloon = 'green'
    elif str(instance.group_name) == 'group_4':
        balloon = 'purple'
        
    data = {
        "user": str(instance.user),
        "bet": instance.bet,
        "multiplier": str(instance.multiplier),
        "won": str(instance.won),
        "balloon":balloon,
        "type":data_type,
    }
    print(data)
    # Call the update_table method in the WebSocket consumer
 # Send the update using Channels' channel layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "table_updates",
        {
            "type": "table.update",
            "data": data,
        }
    )

@receiver(post_save, sender=User)
def create_user_bank_account(sender, instance, created, **kwargs):
    if created:
        Clients.objects.create(user=instance)
        Bank.objects.create(user=instance)
    
        
        
@receiver(post_save, sender=Bank)
def bank_updated(sender, instance, **kwargs):
    print('bank updated')
    # Construct the data for the WebSocket consumer
    data = {
        "user": str(instance.user),
        "balance": str(instance.balance),
        "type":'balance_update',
    }
    user = instance.user
    client = Clients.objects.filter(user=user).first()
    if client is not None:
        channel_name = client.channel_name
        print(channel_name)
        if channel_name is not None:
        
        

            # Send the update to the user's channel
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(
                f"{channel_name}",  # Use a unique channel name per user
                {
                    "type": "balance.update",
                    "data": data,
                    
                }
            )
    
@receiver(post_save, sender=Games)
def game_updated(sender, instance, **kwargs):
    print('New Game signal received')
    # Construct the data for the WebSocket consumer
    print(str(instance.crash_point))
    if str(instance.crash_point) != '':
        print('here')
        data = {
        "type": "multiplier_update",
        "game_hash": str(instance.hash),
        
        "group_name":str(instance.group_name),
        "hash": str(instance.hash),
        "server_seed":str(instance.server_seed),
        "salt":str(instance.salt),
        
        "multiplier":str(instance.crash_point),
            
        }
    else:
    
        data = {
            "type": "new_game",
            "game_hash": str(instance.hash),
        }

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "table_updates",
        {
            "type": "table.update",
            "data": data,
        }
    )
    
@receiver(post_save, sender=Bank)
def update_owners_bank(sender, instance, **kwargs):
    # Whenever a Bank instance is saved, update the OwnersBank balance
    owner_username = 'admin'  # Replace with the actual owner's username
    owners_bank, created = OwnersBank.objects.get_or_create(user=User.objects.get(user_name=owner_username))
    
    if not created:
        owners_bank.update_balance()
    
@receiver(post_save, sender=OwnersBank)
def game_updated(sender, instance, **kwargs):
    print('Owner update')
    
    
    data = {
        "type": "new_update",
        "user":str(instance.user),   
        "users_cash":str(instance.users_cash),
        "float_cash":str(instance.float_cash),
        "total_cash":str(instance.total_cash),
        "revenue":str(instance.total_real),
        "profit":str(instance.profit_to_owner),
    }
    

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "admin_updates",
        {
            "type": "pot.update",
            "data": data,
        }
    )
    

