from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.views import View
from .models import Transactions, BettingWindow, CashoutWindow, Games, Bank, OwnersBank, GameSets, TransactionsForLastGameBet, UsersDepositsandWithdrawals, User, WhoIsAdmin
from .utils import ServerSeedGenerator

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import FormView, View
from .forms import UserCreationForm, UserLoginForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
import random
import string
import time
from .backends import PhoneUsernameAuthenticationBackend as EoP
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from django.conf import settings


# views.py

from django.views.decorators.csrf import csrf_exempt

from django.views import View
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # Import your GameManager module
from .tasks import start_game, stop_game
from django.contrib.auth.decorators import permission_required
import subprocess
import os
import logging
from asgiref.sync import sync_to_async

from django.db.models import Max, Min, Sum, F, ExpressionWrapper, DecimalField, Count, Value
from django.db.models.functions import TruncDate

import json
from django.core.paginator import Paginator
from django.contrib.auth.models import Permission




# Configure the logger
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class StartGameView(View):

    async def start_game(self):
        
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "realtime_group",
            {
                "type": "start.game",
                
            }
        )  # Adjust the delay as needed

    async def get(self, request, *args, **kwargs):
        # Start the game in the background
        await self.start_game()
        
        # Return a response indicating that the game is running
        return JsonResponse({'status': 'Game is running in the background'})




class UserRegistrationView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'sign-up.html'
    success_url = reverse_lazy('login')  # Redirect to login page after successful registration
    success_message = "Your account has been created successfully. You can now log in."

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        bank_account = Bank.objects.get(user=self.request.user)
            
        bank_balance = bank_account.balance 
        return JsonResponse({'success': True, 'balance':bank_balance, 'username':user.user_name}, status=200)
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your registration. Please check the form and try again.')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(FormView):
    form_class = UserLoginForm
    template_name = 'sign-in.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, 'You have successfully logged in!')
        bank_account = Bank.objects.get(user=self.request.user)
            
        bank_balance = bank_account.balance 
        return JsonResponse({'success': True, 'balance':bank_balance, 'username':user.user_name}, status=200)

    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, 'Invalid phone number or password. Please try again.')
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({'authenticated': True, 'redirect_url': reverse_lazy('home')})
        return super().dispatch(request, *args, **kwargs)

        
    
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')  

def get_new_crash_point(request):
    seed_generator = ServerSeedGenerator()
    seed_generator.generate_hash()
    seed_generator.crash_point_from_hash()
    
    crash_point = seed_generator.get_crash_point()
    
    return JsonResponse({'crash_point': crash_point})
class Home(TemplateView):
    model = Transactions
    template_name = 'index.html'
    context_object_name = 'items'
    def __init__(self):
        super().__init__()
        self.username = None
        self.bank_balance = None  
        self.room_name = None

    def get_context_data(self, **kwargs):
        # Fetch and add the Transactions objects to the context
        def generate_random_string(length):
            letters = string.ascii_letters  # Get all letters (both lowercase and uppercase)
            random_string = ''.join(random.choice(letters) for _ in range(length))
            return random_string

        if self.request.user.is_authenticated:
            self.username = self.request.user.user_name
            bank_account = Bank.objects.get(user=self.request.user)
            
            self.bank_balance = bank_account.balance 
            self.room_name = bank_account.account_id
            
            
        else:
            self.username = generate_random_string(8)
            
        last_seven_crash_points = Games.objects.exclude(crash_point='').order_by('-id')[:7]
        
        random_colors = ['#{:02x}{:02x}{:02x}'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(len(last_seven_crash_points))]


        # Create a dictionary to store items and their random colors
        last_seven_dict = {}

        # Update each item in last_seven_crash_points with its random color
        for i, crash_point_data in enumerate(last_seven_crash_points):
            last_seven_dict[crash_point_data] = random_colors[i]
                
            
        self.request.session['username'] = self.username
        items = self.model.objects.all()

       
        context = super().get_context_data(**kwargs)
        context['last_seven_dict'] = last_seven_dict
        context['items'] = items
        context['username'] = self.username
        context['balance'] = self.bank_balance
        context['room_name'] = self.room_name

        # Logging and debugging
       

        return context
    
@method_decorator(csrf_exempt, name='dispatch')
class PlaceBet(View):
    decorators = [csrf_exempt, transaction.atomic]
    @method_decorator(decorators)
    def post(self, request, *args, **kwargs):
        
        betting_window_state, game_id, game_set_id = self.get_betting_window_state(request.POST.get('group_name'))
        if betting_window_state:
            
            
            if self.request.user.is_authenticated:
                bet_amount = request.POST.get('bet_amount')
                print(bet_amount)
                group_name = request.POST.get('group_name')
                user = self.request.user
                
                  # Check if a transaction with the same game_id exists
                if Transactions.objects.filter(game_id=game_id, user=user).exists():
                    # raise ValidationError("A transaction with this game_id already exists.")
                    response_data = {
                    'status': 'error',
                    'message': 'A transaction with this game_id already exists',
                        }
                    return JsonResponse(response_data, status=400)
                if Transactions.objects.filter(game_set_id=game_set_id, user=user).exists():
                    # raise ValidationError("A transaction with this game_set_id already exists.")
                    response_data = {
                    'status': 'error',
                    'message': 'A transaction with this game_set_id already exists',
                        }
                    return JsonResponse(response_data, status=400)
                    
                try:
                    bank_instance = Bank.objects.select_for_update().get(user=user)
                    amount = Decimal(bet_amount)
                    if bank_instance.balance >= amount:
                        bank_instance.balance -= amount
                        bank_instance.save()
                    else:
                        return JsonResponse({'status': 'error', 'message': 'insufficient_funds'}, status=400)
                except Bank.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'no_bank'}, status=400)
                
               
               
                     

                # Create and save the transaction instance
                bet_instance = Transactions(user=user, bet=bet_amount, multiplier=0, won=0, game_id=game_id,game_set_id=game_set_id, bet_placed=True, group_name=group_name)
                bet_instance.save()
                
                response_data = {
                    'status': 'success',
                    'message': 'Bet placed successfully',
                    'bet_amount': bet_amount,
                    'username': user.user_name
                }
                user_count = cache.get("realtime_betting_users_count")
                if user_count is None:
                    user_count = 1
                else:
                    user_count += 1
                cache.set("realtime_betting_users_count", user_count)
                        
                return JsonResponse(response_data, status=200)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Please login to place bet',
                    
                }
                return JsonResponse(response_data, status=400)
        else:
            response_data = {
                'status': 'error',
                'message': 'Bet not placed, betting window closed'
            }
            return JsonResponse(response_data, status=400)
    
    def get_betting_window_state(self, group_name):
        cached_state = cache.get('betting_window_state')
        cached_game_id = cache.get(f'{group_name}_game_id')
        cache_game_set_id = cache.get('game_set_id')
        
        if cached_state is not None and cached_game_id is not None and cache_game_set_id is not None:
            return cached_state, cached_game_id, cache_game_set_id
        
        betting_window, game_id, game_set_id = self.database_fetch_betting_window_state(group_name)
        
       
        
        
        return betting_window, game_id, game_set_id
    
    def database_fetch_betting_window_state(self, group_name):
        betting_window_object = BettingWindow.objects.first()
        betting_window = betting_window_object.is_open
        game_id_object = Games.objects.filter(group_name= group_name).order_by('created_at').last()
        game_set_id_object = GameSets.objects.order_by('created_at').last()
        game_id = game_id_object.game_id
        game_set_id = game_set_id_object.game_set_id
        
        return betting_window, game_id, game_set_id

    
class CashoutView(View):
    
    
    decorators = [csrf_protect, login_required]
    @method_decorator(decorators)
    def get(self, request, *args, **kwargs):
        print('cashout get bet amount called')
        try:
            user_transaction = Transactions.objects.filter(user=request.user).order_by('created_at').last()
            game_id = Games.objects.order_by('created_at').last()
            print('game_id from user', user_transaction.game_id)
            print('game_id from current game:', game_id.game_id)
            if user_transaction.game_id == game_id.game_id:    
                bet_amount = user_transaction.bet
            
            else:
                bet_amount = 0
        except:
            bet_amount = 0
        print('bet_amount',bet_amount)
        return JsonResponse({'bet_amount': bet_amount})
           

    
    decorators = [csrf_protect, login_required, transaction.atomic]
    @method_decorator(decorators)
    def post(self, request, *args, **kwargs):
        cashout_window_state = self.get_cashout_window_state()
        if cashout_window_state:
            multiplier = request.POST.get('multiplier')
            game_id = request.POST.get('game_id')
            user = request.user

            try:
                transaction = Transactions.objects.filter(user=user).order_by('created_at').last()
                games_game_id = Games.objects.order_by('created_at').last()

                if game_id == transaction.game_id == games_game_id.game_id:
                    if not transaction.game_played:
                        transaction.multiplier = multiplier
                        transaction.won = transaction.bet * float(multiplier)
                        transaction.game_played = True
                        transaction.save()

                        try:
                            bank_instance = Bank.objects.select_for_update().get(user=user)
                            bank_instance.balance += Decimal(transaction.won)
                            bank_instance.save()
                        except Bank.DoesNotExist:
                            return JsonResponse({'status': 'error', 'message': 'no_bank'}, status=400)

                        response_data = {
                            'status': 'success',
                            'message': 'Cashout successful'
                        }
                    else:
                        response_data = {
                            'status': 'error',
                            'message': 'User already cashed out'
                        }
                else:
                    response_data = {
                        'status': 'error',
                        'message': 'Non-matching game_id'
                    }

            except Exception as e:
                response_data = {
                    'status': 'error',
                    'message': 'Cashout failed',
                    'error': str(e)
                }
        else:
            response_data = {
                'status': 'error',
                'message': 'Cashout window closed'
            }
        
        return JsonResponse(response_data, status=400 if response_data['status'] == 'error' else 200)
    def get_cashout_window_state(self):
        cached_state = cache.get('cashout_window_state')
        if cached_state is not None:
            return cached_state
        
        cashout_window = self.database_fetch_cashout_window_state()
        cache.set('cashout_window_state', cashout_window, timeout=3600)
        return cashout_window
    
    def database_fetch_cashout_window_state(self):
        cashout_window_object = CashoutWindow.objects.first()
        cashout_window = cashout_window_object.is_open
        return cashout_window
    
    
    
class DepositView(View):
    decorators = [csrf_protect, login_required, transaction.atomic]
    @method_decorator(decorators)
    def post(self, request, *args, **kwargs):
        
       
        deposit_amount = request.POST.get('deposit_amount')
        
        user = request.user
        amount_to_add = Decimal(deposit_amount)

        

        try:
            bank_instance = Bank.objects.select_for_update().get(user=user)
            bank_instance.balance += amount_to_add
            bank_instance.save()
            deposit_instance = UsersDepositsandWithdrawals.objects.create(user=user, deposit=amount_to_add)

            
            response_data = {
                        'status': 'success',
                        'message': 'Deposit successful'
                    }
        except Bank.DoesNotExist:
            response_data =  {'status': 'error', 'message': 'no_bank'}
            

                    
                
        return JsonResponse(response_data, status=400 if response_data['status'] == 'error' else 200)
    
class WithdrawView(View):
    decorators = [csrf_protect, login_required, transaction.atomic]
    @method_decorator(decorators)
    def post(self, request, *args, **kwargs):
        
       
        withdraw_amount = request.POST.get('withdraw_amount')
        
        user = request.user
        amount_to_subtract = Decimal(withdraw_amount)

        

        try:
            bank_instance = Bank.objects.select_for_update().get(user=user)
            bank_instance.balance -= amount_to_subtract
            bank_instance.save()
            withdrawal_instance = UsersDepositsandWithdrawals.objects.create(user=user, withdrawal=amount_to_subtract)

            response_data = {
                        'status': 'success',
                        'message': 'Withdrawal successful'
                    }
        except Bank.DoesNotExist:
            response_data =  {'status': 'error', 'message': 'no_bank'}

                    
                
        return JsonResponse(response_data, status=400 if response_data['status'] == 'error' else 200)
 
# @method_decorator(permission_required('crash.customadminpermission', raise_exception=True), name='dispatch')
# @method_decorator(login_required, name='dispatch')
class AdminView(TemplateView):
    template_name = 'admin2.html'
    
   
    async def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'start':
            try:
                # Find and terminate the 'rungame' process if it's running
                subprocess.run(['pkill', '-f', 'rungame'])

                # Start the game as an asynchronous subprocess
                process = await asyncio.create_subprocess_exec(
                    'python', 'manage.py', 'rungame',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Log the stdout output asynchronously
                async def log_output():
                    async for line in process.stdout:
                        logger.info(line.decode().strip())

                # Start logging the output without waiting for it to complete
                asyncio.create_task(log_output())

                response_data = {'message': 'Game started successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error starting the game: {str(e)}'}
                print(response_data)
                return JsonResponse(response_data, status=500)

        elif action == 'stop':
            try:
                # Find and kill the 'rungame' process
                subprocess.run(['pkill', '-f', 'rungame'])
                response_data = {'message': 'Game stopped successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error stopping the game: {str(e)}'}
                return JsonResponse(response_data, status=500)


        else:
            response_data = {'error': 'Invalid action'}
            return JsonResponse(response_data, status=400)
   
    @sync_to_async
    @method_decorator(permission_required('crash.customadminpermission', raise_exception=True))
    def get_context_data(self,request, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            user = self.request.user
            owners_bank = OwnersBank.objects.get(user=user)
            
            pot_amount = owners_bank.total_cash
            profit = owners_bank.profit_to_owner
            revenue = owners_bank.total_real
            deposits = owners_bank.total_deposits
            withdrawals = owners_bank.total_withdrawals
            players_online = cache.get("realtime_group_user_count")
            players_betting = cache.get("realtime_betting_users_count")
            players_lost = cache.get("bets_lost_user_count")
            players_won = cache.get("bets_won_user_count")
            withdrawals_data = UsersDepositsandWithdrawals.objects.filter(withdrawal__gt=0)
            deposits_data = UsersDepositsandWithdrawals.objects.filter(deposit__gt=0)
            users_data = User.objects.all()
            admins = WhoIsAdmin.objects.all()
            all_bets_in_all_transactions = list(Transactions.objects.all())
            all_bets_in_all_last_balloon_transactions = list(TransactionsForLastGameBet.objects.all())
            all_bets_sorted = sorted(all_bets_in_all_transactions + all_bets_in_all_last_balloon_transactions, key=lambda bet: bet.created_at)

                
            
        
            all_withdrawals = []
            all_deposits = []
            all_users = []
            all_bets = []
            all_admins = []
           
            

            for admin in admins:
                
                
                    # User has the 'crash.customadminpermission' permission
                    print(admin)
                    is_active = 'active' if admin.is_active else 'inactive'
                    admins_dict = {
                         'id':admin.id,
                         'user_name':admin.user.user_name,
                         'created_at':admin.created_at,
                         'phone_number':admin.user.phone_number,
                         'status':is_active,
                         'role': 'admin'
                    }
                    all_admins.append(admins_dict)
            
            for bet in all_bets_sorted:
                
                original_created_at = bet.created_at  # Replace with your actual field
                formatted_created_at = original_created_at.strftime("%Y-%m-%d %H:%M:%S")
                game_id = str(bet.game_id)  # Convert UUID to string
                formatted_uid = game_id[:8]  # Fix the variable name
                bank_data = Bank.objects.get(user=user)
                balance = bank_data.balance

                if bet in all_bets_in_all_transactions:
                    game_type = 'classic'
                else:
                    game_type = 'special'

                bets_dict = {
                    'id': bet.id,
                    'username': bet.user.user_name,
                    'game_id': formatted_uid,
                    'game_set_id': bet.game_set_id,
                    'created_at': formatted_created_at,
                    'game_type': game_type,
                    'bet_amt': bet.bet,
                    'cashout': bet.won,
                    'profit': bet.won - bet.bet,
                    'net_profit': '0',  # You might need to calculate this based on your business logic
                    'result': 'won' if bet.won > 0 and bet.game_played == True else 'lost',
                    'balance': balance
                }
                all_bets.append(bets_dict)

                
             
                
            
            for withdrawal in withdrawals_data:
                original_created_at = withdrawal.created_at  # Replace with your actual field
                formatted_created_at = original_created_at.strftime("%Y-%m-%d %H:%M:%S")
                original_uid = str(withdrawal.uid)  # Convert UUID to string
                formatted_uid = original_uid[:8]

                withdrawal_dict = {
                    'id': withdrawal.id,
                    'uid': formatted_uid,
                    'created_at': formatted_created_at,  # Update 'created_at' with the formatted datetime
                    'phone_number': withdrawal.user.phone_number,
                    'status': withdrawal.status,
                    'amount': withdrawal.withdrawal,
                    'charges': withdrawal.charges,
                    'net': withdrawal.net_amount,
                }
                all_withdrawals.append(withdrawal_dict)
                
           
            for deposit in deposits_data:
                original_created_at = deposit.created_at  # Replace with your actual field
                formatted_created_at = original_created_at.strftime("%Y-%m-%d %H:%M:%S")
                original_uid = str(deposit.uid)  
                formatted_uid = original_uid[:8]

                deposit_dict = {
                    'id': deposit.id,
                    'uid': formatted_uid,
                    'created_at': formatted_created_at, 
                    'phone_number': deposit.user.phone_number,
                    'status':deposit.status,
                    'amount':deposit.deposit,
                    'charges':deposit.charges,
                    'net':deposit.net_amount,
                }
                all_deposits.append(deposit_dict)
            
       
                all_users = []
                for user in users_data:
                    bank_data = Bank.objects.get(user=user)
                    transaction_data = Transactions.objects.filter(user=user).values('won')
                    transactions_for_last_game_data = TransactionsForLastGameBet.objects.filter(user=user).values('won')
                    transactions_counting_losses = Transactions.objects.filter(user=user, game_played=True, won=0).values('bet')

                    account_id = bank_data.account_id
                    print(account_id)
                    balance = bank_data.balance
                    h_gain = max(
                        transaction_data.aggregate(highest=Max(F('won')))['highest'] or 0,
                        transactions_for_last_game_data.aggregate(highest=Max(F('won')))['highest'] or 0
                    )

                    h_loss = max(
                        transactions_counting_losses.aggregate(highest=Max(F('bet')))['highest'] or 0,
                        transactions_counting_losses.aggregate(highest=Max(F('bet')))['highest'] or 0
                    )

                    profit = bank_data.profit_to_user - bank_data.losses_by_user
                    games_played = transaction_data.filter(game_played=True).count() + transactions_for_last_game_data.filter(game_played=True).count()
                    original_created_at = user.created_at  # Replace with your actual field
                    formatted_created_at = original_created_at.strftime("%Y-%m-%d %H:%M:%S")
                    original_uid = str(account_id)  
                    formatted_uid = original_uid[:8]

                    user_data = {
                        'uid': formatted_uid,
                        'level':"1",
                        'username': user.user_name,
                        'phone_number': user.phone_number,
                        'status': "active",
                        'chat_status': "active",
                        'joined_on': formatted_created_at,
                        'balance': balance,
                        'bonus': "0",
                        'h_gain': h_gain,
                        'h_loss': f"-{h_loss}",
                        'profit': profit,
                        'games_played': games_played,
                    }
                    all_users.append(user_data)


            
            items_per_page = 10  # Adjust as needed

            # Create paginator for withdrawals
            paginator_withdrawals = Paginator(all_withdrawals, items_per_page)
            page_number_withdrawals = self.request.GET.get('withdrawals_page')
            withdrawals_page = paginator_withdrawals.get_page(page_number_withdrawals)

            # Create paginator for deposits
            paginator_deposits = Paginator(all_deposits, items_per_page)
            page_number_deposits = self.request.GET.get('deposits_page')
            deposits_page = paginator_deposits.get_page(page_number_deposits)
            
            #Create paginator for users
            
            paginator_users = Paginator(all_users, items_per_page)
            page_number_users = self.request.GET.get('users_page')
            users_page = paginator_users.get_page(page_number_users)
             #Create paginator for bets
            
            paginator_bets = Paginator(all_bets, items_per_page)
            page_number_bets = self.request.GET.get('bets_page')
            bets_page = paginator_bets.get_page(page_number_bets)
            
             #Create paginator for admins
            
            paginator_admins = Paginator(all_admins, items_per_page)
            page_number_admins = self.request.GET.get('admins_page')
            admins_page = paginator_admins.get_page(page_number_admins)



            deposits_by_day = UsersDepositsandWithdrawals.objects.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(total_deposits=Sum('deposit')).order_by('date')

           # Data for Deposits by Day
            deposits_by_day = UsersDepositsandWithdrawals.objects.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(total_deposits=Sum('deposit')).order_by('date')
            deposit_labels = [entry['date'].strftime('%Y-%m-%d') for entry in deposits_by_day]
            deposit_data = [entry['total_deposits'] for entry in deposits_by_day]

            # Data for Withdrawals by Day
            withdrawals_by_day = UsersDepositsandWithdrawals.objects.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(total_withdrawals=Sum('withdrawal')).order_by('date')
            withdrawal_labels = [entry['date'].strftime('%Y-%m-%d') for entry in withdrawals_by_day]
            withdrawal_data = [entry['total_withdrawals'] for entry in withdrawals_by_day]
            deposit_data_float = [float(str(deposit)) for deposit in deposit_data]
            # print(deposit_data_float)
            withdrawal_data_float = [float(str(withdrawal)) for withdrawal in withdrawal_data]
           
            
                        
            context['pot_amount'] = pot_amount
            context['profit'] = profit
            context['revenue'] = revenue
            context['players_online'] = players_online
            context['players_betting'] = players_betting
            context['players_lost'] = players_lost
            context['players_won'] = players_won
            context['deposits'] = deposits
            context['withdrawals'] = withdrawals
            # Add data for deposits and withdrawals graphs to context
            context['deposit_labels'] = deposit_labels            
            context['withdrawal_labels'] = withdrawal_labels
            context['deposit_data'] = deposit_data_float
            context['withdrawal_data'] = withdrawal_data_float
            context['withdrawals_page'] = withdrawals_page
            context['deposits_page'] = deposits_page
            context['users_page'] = users_page
            context['bets_page'] = bets_page
            context['admins_page'] = admins_page

         
            
        except OwnersBank.DoesNotExist:
            return 
            print("OwnersBank record does not exist for the user:", self.request.user)
        
        return context
    
   
    async def get(self, request, *args, **kwargs):
        
        @sync_to_async
        def check_authentication(user):
            if user.is_authenticated:
                try:
                    admin_instance = WhoIsAdmin.objects.get(user=user)
                    return admin_instance is not None
                except WhoIsAdmin.DoesNotExist:
                    return False  # User is not an admin
                except Exception as e:
                    # Handle other potential exceptions (e.g., database connection error)
                    return False
            else:
                return False  # User is not authenticated

            
        if await check_authentication(self.request.user):
            context = await self.get_context_data(request)
            return render(request, self.template_name, context)
        else:
            return render(request, 'adminlogin.html')
        
        
@method_decorator(login_required, name='dispatch')
class BalloonChosenView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        transaction_instance = Transactions.objects.filter(user=user).order_by('created_at').last()
        games_instance = Games.objects.filter(group_name=transaction_instance.group_name).order_by('created_at').last()
        if transaction_instance.game_id == games_instance.game_id:
            print(transaction_instance.group_name)
            response = {
                'group_name': transaction_instance.group_name
                
            }
        else:
            response = {
                'group_name': ''
                
            }
        
        return JsonResponse(response)
    
class TestView(View):
    
    async def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
         
     

        if action == 'start':
            try:
                # Retrieve data from the POST request
                num_users = int(request.POST.get('num_users'))
                risk_factor = int(request.POST.get('risk_factor'))

                    
                        # Find and terminate the 'simulations' process if it's running
                subprocess.run(['pkill', '-f', 'simulations'])

                    # Define the log file path
                file_path = os.path.join(settings.MEDIA_ROOT, 'simulationslog.txt')

                # Open the log file in append mode
                with open(file_path, 'a') as log_file:
                    # Start the game as an asynchronous subprocess and redirect stdout to the log file
                    process = await asyncio.create_subprocess_exec(
                        'python', 'manage.py', 'simulations',
                        f'--risk_factor={risk_factor}', f'--num_users={num_users}',
                        stdout=log_file,  # Redirect stdout to the log file
                        
                    )
                    
                    
                    
            
                

                response_data = {'message': 'Simulation started'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error starting the simulation: {str(e)}'}
                print(response_data)
                return JsonResponse(response_data, status=500)

        elif action == 'stop':
            try:
                # Find and kill the 'rungame' process
                subprocess.run(['pkill', '-f', 'simulations'])
                response_data = {'message': 'Test stopped successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error stopping the game: {str(e)}'}
                return JsonResponse(response_data, status=500)


        else:
            response_data = {'error': 'Invalid action'}
            return JsonResponse(response_data, status=400)
  
  
@login_required   
def download_users_json(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'simulationslog.txt')

    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/plain')  # Use 'text/plain' for a plain text file
            response['Content-Disposition'] = f'attachment; filename=simulationslog.txt'  # Correct filename
            return response
    else:
        return HttpResponse('The file does not exist.', status=404)   
        
# @login_required   
# def download_users_json(request):
#     # Path to the users.json file in the media directory
#     file_path = os.path.join(settings.MEDIA_ROOT, 'users.json')

#     # Check if the file exists
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='application/json')
#             response['Content-Disposition'] = f'attachment; filename=users.json'
#             return response
#     else:
#         return HttpResponse('The file does not exist.', status=404)

class AdminViewWithRespawn(TemplateView):
    template_name = 'theadminwithrespawn.html'


    async def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        respawn = request.POST.get('respawn')
        if respawn == 'true':
            try:
                # Find and terminate the 'rungame' process if it's running
                subprocess.run(['pkill', '-f', 'respawn'])

                # Start the game as an asynchronous subprocess
                process = await asyncio.create_subprocess_exec(
                    'python', 'manage.py', 'respawn',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Log the stdout output asynchronously
                async def log_output():
                    async for line in process.stdout:
                        logger.info(line.decode().strip())

                # Start logging the output without waiting for it to complete
                asyncio.create_task(log_output())

                response_data = {'message': 'Respawn started successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error starting the respawn: {str(e)}'}
                print(response_data)
                return JsonResponse(response_data, status=500)
        elif respawn == 'false':
            try:
                # Find and kill the 'rungame' process
                subprocess.run(['pkill', '-f', 'respawn'])
                response_data = {'message': 'respawn stopped successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error stopping the respawn: {str(e)}'}
                return JsonResponse(response_data, status=500)
            

        if action == 'start':
            try:
                # Find and terminate the 'rungame' process if it's running
                subprocess.run(['pkill', '-f', 'rungame'])

                # Start the game as an asynchronous subprocess
                process = await asyncio.create_subprocess_exec(
                    'python', 'manage.py', 'rungame',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Log the stdout output asynchronously
                async def log_output():
                    async for line in process.stdout:
                        logger.info(line.decode().strip())

                # Start logging the output without waiting for it to complete
                asyncio.create_task(log_output())

                response_data = {'message': 'Game started successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error starting the game: {str(e)}'}
                print(response_data)
                return JsonResponse(response_data, status=500)

        elif action == 'stop':
            try:
                # Find and kill the 'rungame' process
                subprocess.run(['pkill', '-f', 'rungame'])
                response_data = {'message': 'Game stopped successfully.'}
                return JsonResponse(response_data, status=200)
            except Exception as e:
                response_data = {'error': f'Error stopping the game: {str(e)}'}
                return JsonResponse(response_data, status=500)


        else:
            response_data = {'error': 'Invalid action'}
            return JsonResponse(response_data, status=400)
        

    @sync_to_async
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            user = self.request.user
            owners_bank = OwnersBank.objects.get(user=user)
            pot_amount = owners_bank.total_cash
            profit = owners_bank.profit_to_owner
            revenue = owners_bank.total_real
            players_online = cache.get("realtime_group_user_count")
            players_betting = cache.get("realtime_betting_users_count")
            players_lost = cache.get("bets_lost_user_count")
            players_won = cache.get("bets_won_user_count")
            
            context['pot_amount'] = pot_amount
            context['profit'] = profit
            context['revenue'] = revenue
            context['players_online'] = players_online
            context['players_betting'] = players_betting
            context['players_lost'] = players_lost
            context['players_won'] = players_won
            
        except OwnersBank.DoesNotExist:
            return 
            print("OwnersBank record does not exist for the user:", self.request.user)
        
        return context
    
      
    async def get(self, request, *args, **kwargs):
        
        @sync_to_async 
        def check_authentication(user):
            if self.request.user.is_authenticated:
                return True
            
        if await check_authentication(self.request.user):
            context = await self.get_context_data()
            return render(request, self.template_name, context)
        else:
            return render(request, 'adminlogin.html')
class TopWinnersView(View):
    def get(self, request, *args, **kwargs):
        # Get the top 5 transactions with the highest 'won' values
        top_5_transactions = Transactions.objects.filter(game_played=True).order_by('-won')[:5]

        # Serialize the transaction data to JSON
        top_winners_data = [{
            'user': transaction.user.user_name,
            'bet': transaction.bet,
            'multiplier': float(transaction.multiplier),
            'won': float(transaction.won),
            'balloon': self.get_balloon_color(transaction.group_name),
            # Add other fields as needed
        } for transaction in top_5_transactions]
        
        # print(top_winners_data)

        # Return the data as JSON response
        return JsonResponse(top_winners_data, safe=False)
    
    def get_balloon_color(self, group_name):
        if group_name == 'group_1':
            return 'blue'
        elif group_name == 'group_2':
            return 'red'
        elif group_name == 'group_3':
            return 'green'
        else:
            return 'purple'
    
    
@method_decorator(login_required, name='dispatch')
class UserBetsView(View):
    def get(self, request, *args, **kwargs):
        user = self.request.user

        # Retrieve the top 10 transactions for the logged-in user
        top_10_transactions = Transactions.objects.filter(user=user, game_played=True).order_by('-created_at')[:10]

        # Serialize the transaction data to JSON
        user_bets_data = [{
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format the date as needed
            'game_id': transaction.game_id,
            'stake': float(transaction.bet),
            'multiplier': float(transaction.multiplier),
            'balloon': self.get_balloon_color(transaction.group_name),
            'won': float(transaction.won),
            # Add other fields as needed
        } for transaction in top_10_transactions]

        # Return the data as JSON response
        return JsonResponse(user_bets_data, safe=False)

    def get_balloon_color(self, group_name):
        if group_name == 'group_1':
            return 'blue'
        elif group_name == 'group_2':
            return 'red'
        elif group_name == 'group_3':
            return 'green'
        else:
            return 'purple'

@method_decorator(login_required, name='dispatch')
class BetOnLastBalloon(View):
   
    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(self.request)
        print(request.POST)
        print(request.POST.get('group_name'))
        
        betting_window_state, game_id, game_set_id = self.get_betting_window_state(request.POST.get('group_name'))
        
        if betting_window_state:
            if self.request.user.is_authenticated:
            
                group_name = request.POST.get('group_name')
                bet_amount = request.POST.get('bet_amount')
                user = self.request.user
                
                  # Check if a transaction with the same game_id exists
                if TransactionsForLastGameBet.objects.filter(game_id=game_id, user=user).exists():
                    # raise ValidationError("A transaction with this game_id already exists.")
                    response_data = {
                    'status': 'error',
                    'message': 'A transaction with this game_id already exists',
                        }
                    return JsonResponse(response_data, status=400)
                if TransactionsForLastGameBet.objects.filter(game_set_id=game_set_id, user=user).exists():
                    # raise ValidationError("A transaction with this game_set_id already exists.")
                    response_data = {
                    'status': 'error',
                    'message': 'A transaction with this game_set_id already exists',
                        }
                    return JsonResponse(response_data, status=400)
                    
                try:
                    with transaction.atomic():
                        bank_instance = Bank.objects.select_for_update().get(user=user)
                        amount = Decimal(bet_amount)
                        if bank_instance.balance >= amount:
                            bank_instance.balance -= amount
                            bank_instance.save()
                        else:
                            return JsonResponse({'status': 'error', 'message': 'insufficient_funds'}, status=400)
                except Bank.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'no_bank'}, status=400)
                
               
               
                     

                # Create and save the transaction instance
                bet_instance = TransactionsForLastGameBet(user=user, bet=bet_amount, game_id=game_id,game_set_id=game_set_id, bet_placed=True, balloon_betted_on=group_name)
                bet_instance.save()
                
                response_data = {
                    'status': 'success',
                    'message': 'Bet placed successfully',
                    'bet_amount': bet_amount,
                    'username': user.user_name
                }
                user_count = cache.get("realtime_betting_users_count")
                if user_count is None:
                    user_count = 1
                else:
                    user_count += 1
                cache.set("realtime_betting_users_count", user_count)
                        
                return JsonResponse(response_data, status=200)
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Please login to place bet',
                    
                }
                return JsonResponse(response_data, status=400)
        else:
            response_data = {
                'status': 'error',
                'message': 'Bet not placed, betting window closed'
            }
            return JsonResponse(response_data, status=400)
        
        
        
    def get_betting_window_state(self, group_name):
        cached_state = cache.get('betting_window_state')
        cached_game_id = cache.get(f'{group_name}_game_id')
        cache_game_set_id = cache.get('game_set_id')
        
        if cached_state is not None and cached_game_id is not None and cache_game_set_id is not None:
            return cached_state, cached_game_id, cache_game_set_id
        
        # betting_window, game_id, game_set_id = self.database_fetch_betting_window_state(group_name)
        
       
        
        
        # return betting_window, game_id, game_set_id
    
    def database_fetch_betting_window_state(self, group_name):
        betting_window_object = BettingWindow.objects.first()
        betting_window = betting_window_object.is_open
        game_id_object = Games.objects.filter(group_name= group_name).order_by('created_at').last()
        game_set_id_object = GameSets.objects.order_by('created_at').last()
        game_id = game_id_object.game_id
        game_set_id = game_set_id_object.game_set_id
        
        return betting_window, game_id, game_set_id
    