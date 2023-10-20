import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer



import time

from .models import Clients, Transactions, Bank, Games, User, TransactionsForLastGameBet
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import transaction
from decimal import Decimal
from django.core.cache import cache
from .tasks import start_game, stop_game, data_to_admin


class RealtimeUpdatesConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.count = 0

	async def connect(self):
		
		self.group_name = "realtime_group"
		await self.channel_layer.group_add(self.group_name, self.channel_name)
		await self.accept()
	   # Increment the user count when a new user connects
		await self.increment_user_count()
		
		# Dictionary that maps group names to cache keys
		group_game_multipliers = {
			'group_1': 'group_1_game_multiplier',
			'group_2': 'group_2_game_multiplier',
			'group_3': 'group_3_game_multiplier',
			'group_4': 'group_4_game_multiplier',
		}

		# Initialize an empty tuple to store valid group names
		validgames = []

		# Iterate through the group_game_multipliers
		for group, cache_key in group_game_multipliers.items():
			cached_multiplier = cache.get(cache_key)  # Retrieve the cached multiplier
			print(cached_multiplier)  # For debugging purposes

			# Check the value of the cached multiplier and take appropriate action
			if cached_multiplier == 'Popped':
				pass  # Do nothing for 'Popped'
			elif cached_multiplier == 'Wait for new game':
				pass  # Do nothing for 'Wait for new game'
			elif cached_multiplier is None:
				pass  # Do nothing if the multiplier is None
			else:
				validgames.append(group)  # Add the group to validgames if the multiplier is valid
    
		if validgames:

			# Get the cached multiplier for the first valid group
			
			cached_multiplier = cache.get(f"{validgames[0]}_game_multiplier")
			# Create a tuple of valid balloon colors based on group names
			valid_balloons = []
			for group in validgames:
     
				if group == 'group_1':
					valid_balloons.append('0x54deff')
				elif group == 'group_2':
					valid_balloons.append('0xff0000')
				elif group == 'group_3':
					valid_balloons.append('0x00ff00')
				elif group == 'group_4':
					valid_balloons.append('0x800080')
			print(valid_balloons)
			# Send a message with relevant data
			await self.send(text_data=json.dumps({
				'type': 'ongoing_synchronizer',
				'cached_multiplier': cached_multiplier,
				'group_name': validgames[0],
				'valid_balloons': valid_balloons,
				'message': 'ongoing',
			}))

		
	
		

		data_to_admin.delay()
		
		
	async def increment_user_count(self):
		# Use a cache or a database to store and update the user count
		# For example, you can use Django's cache framework:
		user_count = cache.get("realtime_group_user_count")
		if user_count is None:
			user_count = 1
		else:
			user_count += 1
		cache.set("realtime_group_user_count", user_count)

	async def decrement_user_count(self):
		# Use a cache or a database to decrement the user count
		# For example, you can use Django's cache framework:
		user_count = cache.get("realtime_group_user_count")
		if user_count is not None:
			user_count -= 1
			if user_count <= 0:
				# Optionally, you can remove the count key when there are no users
				cache.delete("realtime_group_user_count")
			else:
				cache.set("realtime_group_user_count", user_count)
   

	async def disconnect(self, close_code):
		await self.decrement_user_count()
		await self.channel_layer.group_discard(self.group_name, self.channel_name)
		
	async def realtime_update(self, event):
		# print('game new update')
		updated_item = event['data']
		await self.send(text_data=json.dumps(updated_item))
		
	
	
	@database_sync_to_async
	def update_game_on_crash(self, group_name, game_id):
		
		try:
			with transaction.atomic():
				if self.count > 4:
					self.count = 0
				self.count += 1
				print(self.count)
				users_transactions = Transactions.objects.filter(group_name=group_name, game_id=game_id)

				self.update_transactions(users_transactions, 1)
				if self.count == 4:
					self.count = 0
					game_set_id = cache.get('game_set_id')
					
					last_game_transactions = TransactionsForLastGameBet.objects.filter(game_set_id=game_set_id)

					print(last_game_transactions)
					last_balloon_transactions = TransactionsForLastGameBet.objects.filter(balloon_betted_on=group_name, game_id=game_id)
					print(last_balloon_transactions)

					self.update_transactions(last_game_transactions, 2, last_balloon_transactions)
				
		except Exception as e:
			print("An error occurred:", str(e))
   
   
	def update_transactions(self, transactions, multiplier, last_balloon_transactions=None):
		print('update_transactions_called')
		try:
			for new_transaction in transactions:
				if not new_transaction.game_played:
					new_transaction.game_played = True
					if multiplier == 1:
						print('multiplier=1')
						new_transaction.save()
					elif multiplier == 2:
						print('multiplier=2')
						if new_transaction in last_balloon_transactions:
							new_transaction.won = Decimal(new_transaction.bet) * multiplier
						else:
							print('userlostbet')
							new_transaction.won = 0
						new_transaction.save()

					# Update the user's bank record
					user_bank = Bank.objects.get(user=new_transaction.user)
					if multiplier == 1:
						user_bank.losses_by_user += Decimal(new_transaction.bet)
					elif multiplier == 2:
						if new_transaction in last_balloon_transactions:
							user_bank.balance += Decimal(new_transaction.won)
							user_bank.profit_to_user += Decimal(new_transaction.won)
						else:
							user_bank.losses_by_user += Decimal(new_transaction.bet)
					user_bank.save()
		except Transactions.DoesNotExist:
			print("Transaction does not exist.")
		except Bank.DoesNotExist:
			print("Bank does not exist.")

				
	task = None 
	async def game_crashed(self, event):
        # If there's an existing task, cancel it
		if self.task:
			self.task.cancel()

		data = event['data']
		group_name = data['group_name']
		game_id = data['game_id']
		crash_point = data['crash_point']
		await self.update_game_on_crash(group_name, game_id)
		# Dictionary that maps group names to cache keys
		group_game_multipliers = {
			'group_1': 'group_1_game_multiplier',
			'group_2': 'group_2_game_multiplier',
			'group_3': 'group_3_game_multiplier',
			'group_4': 'group_4_game_multiplier',
		}

		# Initialize an empty tuple to store valid group names
		validgames = []

		# Iterate through the group_game_multipliers
		for group, cache_key in group_game_multipliers.items():
			cached_multiplier = cache.get(cache_key)  # Retrieve the cached multiplier
			print(cached_multiplier)  # For debugging purposes

			# Check the value of the cached multiplier and take appropriate action
			if cached_multiplier == 'Popped':
				pass  # Do nothing for 'Popped'
			elif cached_multiplier == 'Wait for new game':
				pass  # Do nothing for 'Wait for new game'
			elif cached_multiplier is None:
				pass  # Do nothing if the multiplier is None
			else:
				validgames.append(group)  # Add the group to validgames if the multiplier is valid
	
		if validgames:

			# Get the cached multiplier for the first valid group
			
			cached_multiplier = cache.get(f"{validgames[0]}_game_multiplier")
			# Create a tuple of valid balloon colors based on group names
			valid_balloons = []
			for group in validgames:
	
				if group == 'group_1':
					valid_balloons.append('0x54deff')
				elif group == 'group_2':
					valid_balloons.append('0xff0000')
				elif group == 'group_3':
					valid_balloons.append('0x00ff00')
				elif group == 'group_4':
					valid_balloons.append('0x800080')
			print(valid_balloons)

			
			await self.send(text_data=json.dumps({
				'type': 'ongoing_synchronizer',
				'crash_point': crash_point,
				'group_name': group_name,
				'valid_balloons': valid_balloons,
				'message': 'crashed',
			}))
		else:
			await self.send(text_data=json.dumps({
				'type': 'ongoing_synchronizer',
				'crash_point': crash_point,
				'group_name': group_name,
				
				'message': 'crashed',
			}))

		# Create a new task for ongoing_send
		self.task = asyncio.create_task(self.ongoing_send())

	async def ongoing_send(self):
		try:
			await asyncio.sleep(5)  # Sleep for 5 seconds
			print("Task completed")
			
			# Dictionary that maps group names to cache keys
			group_game_multipliers = {
				'group_1': 'group_1_game_multiplier',
				'group_2': 'group_2_game_multiplier',
				'group_3': 'group_3_game_multiplier',
				'group_4': 'group_4_game_multiplier',
			}

			# Initialize an empty tuple to store valid group names
			validgames = []

			# Iterate through the group_game_multipliers
			for group, cache_key in group_game_multipliers.items():
				cached_multiplier = cache.get(cache_key)  # Retrieve the cached multiplier
				print(cached_multiplier)  # For debugging purposes

				# Check the value of the cached multiplier and take appropriate action
				if cached_multiplier == 'Popped':
					pass  # Do nothing for 'Popped'
				elif cached_multiplier == 'Wait for new game':
					pass  # Do nothing for 'Wait for new game'
				elif cached_multiplier is None:
					pass  # Do nothing if the multiplier is None
				else:
					validgames.append(group)  # Add the group to validgames if the multiplier is valid
		
			if validgames:

				# Get the cached multiplier for the first valid group
				
				cached_multiplier = cache.get(f"{validgames[0]}_game_multiplier")
				# Create a tuple of valid balloon colors based on group names
				valid_balloons = []
				for group in validgames:
		
					if group == 'group_1':
						valid_balloons.append('0x54deff')
					elif group == 'group_2':
						valid_balloons.append('0xff0000')
					elif group == 'group_3':
						valid_balloons.append('0x00ff00')
					elif group == 'group_4':
						valid_balloons.append('0x800080')
				print(valid_balloons)

				# Send a message with relevant data
				await self.send(text_data=json.dumps({
					'type': 'ongoing_synchronizer',
					'cached_multiplier': cached_multiplier,
					'group_name': validgames[0],
					'valid_balloons': valid_balloons,
					'message': 'ongoing',
				}))

		except asyncio.CancelledError:
			print("Task was cancelled")
		
		

	

	async def receive(self, text_data):
		# Do nothing with received data
		pass
class GameConsumer(AsyncWebsocketConsumer):
	
	
	async def connect(self):
		if self.scope["user"].is_authenticated:
			# Continue with the WebSocket connection
			
			self.username = self.scope["user"].user_name
			  
			print(f"User {self.username} connected to game room")
		else:
			pass
		self.group_name = self.scope['url_route']['kwargs']['group_name']

		# Add the user to the group
		await self.accept() 
		await self.channel_layer.group_add(
			self.group_name,
			self.channel_name
		)        
		 
	   
			
			
		
	 
		
   
	
  
		

	async def disconnect(self, close_code):
		# Leave room group
		
		await self.channel_layer.group_discard(self.group_name, self.channel_name)

	  

	async def receive(self, text_data):
		try:
			print('receive called')
			print(text_data) 
			data = json.loads(text_data)
			message_type = data.get('type', '')
			print(data)
			
		
			if message_type == "crash_instruction":
				await self.handle_crash_instruction(data)
			elif message_type == "start_synchronizer":
				await self.handle_start_synchronizer(data)
			elif message_type == "cashout_validate":
				response = await self.handle_multiplier_validation(data)
				if response:
					await self.update_cashout(data)
					
			
		except Exception as e:
			print(f"Error in receive: {str(e)}")
			
	async def handle_multiplier_validation(self, data):
		sent_game_id = data.get('game_id')
		sent_multiplier = data.get('multiplier')
		if 'user_name' in data:
			
			
			# Check if 'password' matches a secure hash (not in plaintext)
			password = data.get('password')
			if not password == 'qwertyadu':
				return False
			
		print('sent_multiplier',sent_multiplier)
		print(self.group_name)
		cached_multiplier = cache.get(f'{self.group_name}_game_multiplier')
		print('cached_multiplier', cached_multiplier)
		cashout_window = cache.get(f'{self.group_name}_cashout_window_state')
		print(cashout_window)

		if cashout_window:
			return True
		else:
			
			print("Window closed or received multiplier doesn't match the current game.")
			return False

	@database_sync_to_async
	def update_cashout(self, data):
		with transaction.atomic():
			user = self.scope["user"]
			if user.is_anonymous:
				if 'user_name' in data:
					user_name = data.get('user_name')
					  # Corrected to call the save() method
				   
				else:
					return
			else:
				
				user_name = user.user_name
				pass
				
			print(user)
				
		
			try:
				user = User.objects.get(user_name=user_name)
				new_transaction = Transactions.objects.filter(user=user).order_by('created_at').last()
				games_game_id = Games.objects.filter(group_name= self.group_name).order_by('created_at').last()
				multiplier = cache.get(f'{self.group_name}_game_multiplier')
				
				print('placed_bet_game_id', new_transaction.game_id)
				print('game_id for respective grp', games_game_id.game_id)

				if new_transaction.game_id == games_game_id.game_id:
					if not new_transaction.game_played:
						new_transaction.multiplier = multiplier
						new_transaction.won = new_transaction.bet * float(multiplier)
						new_transaction.game_played = True
						new_transaction.group_name = self.group_name
						new_transaction.save()

						try:
							bank_instance = Bank.objects.select_for_update().get(user=user)
							bank_instance.balance += Decimal(new_transaction.won)
							bank_instance.profit_to_user += Decimal(new_transaction.won)
							bank_instance.save()
						except Bank.DoesNotExist:
							response_data = {'type':'cashout', 'status': 'error', 'message': 'no_bank'}

						response_data = {
							'type':'cashout',
							'status': 'success',
							'message': 'Cashout successful'
						}
						
            
					else:
						response_data = {
							'type':'cashout',
							'status': 'error',
							'message': 'User already cashed out'
						}
				else:
					response_data = {
						'type':'cashout',
						'status': 'error',
						'message': 'Non-matching game_id'
					}

			except Exception as e:
				response_data = {
					'type':'cashout',
					'status': 'error',
					'message': 'Cashout failed',
					'error': str(e)
	
				  }
				
			client = Clients.objects.filter(user=user).first()
		channel_name = client.channel_name
		print(channel_name)
		
		

		# Send the update to the user's channel
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.send)(
			f"{channel_name}",  # Use a unique channel name per user
			{
				"type": "balance.update",
				"data": response_data,
				
			}
		)

	async def game_update(self, event):
		# print('game update')
		updated_item = event['data']
		# print(updated_item)
		await self.send(text_data=json.dumps(updated_item))
	
	async def handle_crash_instruction(self, data):
		# Handle crash instruction here, e.g., trigger the crash action in the game
		await self.send(text_data=json.dumps({
			'message': 'Crash instruction received'
		}))
		await self.close()

	async def handle_start_synchronizer(self, data):
		count = data.get('count', 0)
		for count_value in range(count, -1, -1):
			await self.send(text_data=json.dumps({
				'message': f'Game starts in {count_value}'
			}))

	async def handle_ongoing_synchronizer(self, data):
		current_multiplier = data.get('currentMultiplier', 0)
		# Use the currentMultiplier to render the ongoing graph
		# You can call the renderOngoingGraph function here or include the rendering logic directly
		await self.send(text_data=json.dumps({
			'message': f'Rendering ongoing graph for multiplier {current_multiplier}'
		}))
   

class TableUpdateConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
		self.group_name = "table_updates"
		await self.channel_layer.group_add(self.group_name, self.channel_name)

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.group_name, self.channel_name)

	async def table_update(self, event):
		# print('table update')
		updated_item = event['data']
		await self.send(text_data=json.dumps(updated_item))

	async def update_table(self, data):
		# print('update_data called')
		await self.channel_layer.group_send(self.group_name, {
			"type": "table.update",
			"data": data,
		})

	async def receive(self, text_data):
		# Do nothing with received data
		pass
	
	
class BalanceUpdateConsumer(AsyncWebsocketConsumer):
	
	async def connect(self):
		await self.accept()
		await self.assign_channel_to_user()

	async def disconnect(self, close_code):
		await self.delete_channel_for_user()

	async def assign_channel_to_user(self):
		user = self.scope["user"]
		if user.is_authenticated:
			print('user is authenticated')
			client = await self.update_client(user, self.channel_name)
			print('channel_name:', client.channel_name)

	async def delete_channel_for_user(self):
		user = self.scope["user"]
		if user.is_authenticated:
			await self.delete_client(user)

	@database_sync_to_async
	def update_client(self, user, channel_name):
		with transaction.atomic():
			client, created = Clients.objects.get_or_create(user=user)
			client.channel_name = channel_name
			client.save()
			return client


	@database_sync_to_async
	def delete_client(self, user):
		with transaction.atomic():
			Clients.objects.filter(user=user).delete()

	async def receive(self, text_data):
		# Handle received data
		pass

	async def balance_update(self, event):
		# Handles the "balance.update" event when it's sent to us.
		# print('balance update')
		updated_item = event['data']
		await self.send(text_data=json.dumps(updated_item))

class AdminUpdatesConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		
		self.group_name = "admin_updates"
		await self.channel_layer.group_add(self.group_name, self.channel_name)
		await self.accept()
		
		
   

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.group_name, self.channel_name)
		
	async def pot_update(self, event):
		
		updated_item = event['data']
		await self.send(text_data=json.dumps(updated_item))
		
	
	   

	

	async def receive(self, text_data):
		# Do nothing with received data
		pass
