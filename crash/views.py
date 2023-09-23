from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.views import View
from .models import Transactions, BettingWindow, CashoutWindow, Games, Bank, OwnersBank
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


# views.py

from django.views.decorators.csrf import csrf_exempt

from django.views import View
import asyncio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # Import your GameManager module
from .tasks import start_game, stop_game
from django.contrib.auth.decorators import permission_required
import subprocess
import logging
from asgiref.sync import sync_to_async



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
        return JsonResponse({'success': True, 'balance':bank_balance}, status=200)
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
            
        last_seven_crash_points = Games.objects.exclude(crash_point='').order_by('-id')[:10]
        
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
        
        betting_window_state, game_id = self.get_betting_window_state(request.POST.get('group_name'))
        if betting_window_state:
            
            
            if self.request.user.is_authenticated:
                bet_amount = request.POST.get('bet_amount')
                print(bet_amount)
                group_name = request.POST.get('group_name')
                user = self.request.user
                  # Check if a transaction with the same game_id exists
                if Transactions.objects.filter(game_id=game_id, user=user).exists():
                    raise ValidationError("A transaction with this game_id already exists.")
                    response_data = {
                    'status': 'error',
                    'message': 'A transaction with this game_id already exists',
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
                bet_instance = Transactions(user=user, bet=bet_amount, multiplier=0, won=0, game_id=game_id, bet_placed=True, group_name=group_name)
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
        
        if cached_state is not None and cached_game_id is not None:
            return cached_state, cached_game_id
        
        betting_window, game_id = self.database_fetch_betting_window_state(group_name)
        
        cache.set('betting_window_state', betting_window, timeout=3600)
        cache.set('game_id', game_id, timeout=3600)
        
        return betting_window, game_id
    
    def database_fetch_betting_window_state(self, group_name):
        betting_window_object = BettingWindow.objects.first()
        betting_window = betting_window_object.is_open
        game_id_object = Games.objects.filter(group_name= group_name).order_by('created_at').last()
        game_id = game_id_object.game_id
        
        return betting_window, game_id

    
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