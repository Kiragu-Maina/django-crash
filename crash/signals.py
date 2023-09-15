from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Transactions, User, Bank, Clients, Games

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



@receiver(post_save, sender=Transactions)
def transaction_saved(sender, instance, **kwargs):
    # Construct the data that you want to send to the WebSocket consumer
    print('signals called')
    data = {
        "user": str(instance.user),
        "bet": instance.bet,
        "multiplier": str(instance.multiplier),
        "won": str(instance.won),
        "type":"table_update",
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
    channel_name = client.channel_name
    print(channel_name)
    
    

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