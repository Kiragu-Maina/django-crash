from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Transactions, User, Bank, Clients, Games, OwnersBank, GameSets

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal
from .tasks import start_game, stop_game, data_to_admin
import time
from django.db import transaction
from django.core.cache import cache

@receiver(post_save, sender=Transactions)
def transaction_saved(sender, instance, **kwargs):
    # Construct the data that you want to send to the WebSocket consumer
    
    def update_table(instance):

        if instance.game_played == True:
            if instance.won > 0:
                data_type ="table_update"
                user_count = cache.get("bets_won_user_count")
                if user_count is None:
                    user_count = 1
                else:
                    user_count += 1
                cache.set("bets_won_user_count", user_count)
        
                
            elif instance.won == 0:
                data_type ="lose_update"
                user_count = cache.get("bets_lost_user_count")
                if user_count is None:
                    user_count = 1
                else:
                    user_count += 1
                cache.set("bets_lost_user_count", user_count)
            else:
                data_type ="lose_update"
                user_count = cache.get("bets_lost_user_count")
                if user_count is None:
                    user_count = 1
                else:
                    user_count += 1
                cache.set("bets_lost_user_count", user_count)
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
     
        return data
        
   
    def send_data_to_websocket(data):
        # Send the update using Channels' channel layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "table_updates",
            {
                "type": "table.update",
                "data": data,
            }
        )
       

    # Define a function to be called when the transaction is successfully committed
    def on_commit_callback():
        data = update_table(instance)  # Call the update_table function
       
        send_data_to_websocket(data)
        data_to_admin.delay()
        
        
        
        

    # Use transaction.on_commit to ensure the callback is executed after the transaction
    transaction.on_commit(on_commit_callback)


@receiver(post_save, sender=User)
def create_user_bank_account(sender, instance, created, **kwargs):
  
    def update_client(instance, created):
        
        Clients.objects.create(user=instance)
        Bank.objects.create(user=instance)
    if created:
        transaction.on_commit(lambda: update_client(instance, created))
        
        
            
            
@receiver(post_save, sender=Bank)
def bank_updated(sender, instance, **kwargs):
   
    # Construct the data for the WebSocket consumer
    def update_balance(instance):
        data = {
            "user": str(instance.user),
            "balance": str(instance.balance),
            "type":'balance_update',
        }
        user = instance.user
        client = Clients.objects.filter(user=user).first()
        if client is not None:
            channel_name = client.channel_name
            
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
    transaction.on_commit(lambda: update_balance(instance))
    
@receiver(post_save, sender=Games)
def game_updated(sender, instance, **kwargs):
    
    # Construct the data for the WebSocket consumer
    def update_game(instance):
    
        if str(instance.crash_point) != '':
        
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
    transaction.on_commit(lambda: update_game(instance))
    
@receiver(post_save, sender=Bank)
def update_owners_bank(sender, instance, **kwargs):
    # Whenever a Bank instance is saved, update the OwnersBank balance
    
    def update_owners(instance):
        admin = '0714313598'  # Replace with the actual owner's username
        owners_bank, created = OwnersBank.objects.get_or_create(user=User.objects.get(phone_number=admin))
        
        if not created:
            owners_bank.update_balance()
    transaction.on_commit(lambda: update_owners(instance))
    
@receiver(post_save, sender=OwnersBank)
def admin_updated(sender, instance, **kwargs):
    
    
    def update_admin(instance):
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
    transaction.on_commit(lambda: update_admin(instance))

