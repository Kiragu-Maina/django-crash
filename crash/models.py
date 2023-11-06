from django.db import models
from django.db.models import Sum

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
import re
import datetime
import django.utils.timezone
import uuid
phone_validator = RegexValidator(r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$", "The phone number provided is invalid")

from django.contrib.auth.models import Permission
from django.db import IntegrityError 




class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, user_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number field must be set")
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, user_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, user_name, password, **extra_fields)
    import re

    def normalize_phone_number(self, phone_number):
        # Remove non-numeric characters
        cleaned_number = re.sub(r'\D', '', phone_number)

        # Remove leading '0' and country code if present
        if cleaned_number.startswith('0'):
            cleaned_number = cleaned_number[1:]
        elif cleaned_number.startswith('254'):
            cleaned_number = cleaned_number[3:]

        # Ensure the number is 10 digits long
        if len(cleaned_number) == 9:
            normalized_number = '0' + cleaned_number
            return normalized_number
        else:
            # Handle invalid or unexpected input
            return None

class User(AbstractBaseUser, PermissionsMixin):
    
    phone_number = models.CharField(max_length=16, validators=[phone_validator], unique=True)
    user_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    # is_translator = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
       
        return str(self.user_name)

    

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value
        
class WhoIsAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
   


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.IntegerField()
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    won = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    game_id = models.CharField(max_length=200)
    game_set_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    game_played = models.BooleanField(default=False)
    bet_placed = models.BooleanField(default=False)
    group_name = models.CharField(max_length=200,default='')
    

    def __str__(self):
        return str(self.user)
    
class TransactionsForLastGameBet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balloon_betted_on = models.CharField(max_length=200,default='')
    bet = models.IntegerField()
    won = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    game_id = models.CharField(max_length=200)
    game_set_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    game_played = models.BooleanField(default=False)
    bet_placed = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)
    
    

class Bank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id = models.UUIDField(default=uuid.uuid4, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=50000)
    profit_to_user = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    losses_by_user = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class UsersDepositsandWithdrawals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    withdrawal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=None, default='')
    
class GameSets(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    game_set_id = models.CharField(max_length=200)

class OwnersBank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id = models.UUIDField(default=uuid.uuid4, editable=False)
    users_cash = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    amount_won_by_users = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    amount_lost_by_users = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    float_cash = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    total_cash = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    profit_to_owner = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    total_real = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    total_deposits = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True)
    total_withdrawals = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True)

    def update_balance(self):
            try:
                # Calculate the total balance by aggregating the 'balance' field in Bank models
                # Calculate total balance
                total_balance = Bank.objects.aggregate(total_balance=Sum('balance'))['total_balance']

                # Calculate total amount out (profit_to_user)
                amount_out = Bank.objects.aggregate(total_amount_out=Sum('profit_to_user'))['total_amount_out']

                # Calculate total amount in (losses_by_user)
                amount_in = Bank.objects.aggregate(total_amount_in=Sum('losses_by_user'))['total_amount_in']
               # Calculate total deposits
                deposits = UsersDepositsandWithdrawals.objects.aggregate(total_deposits=Sum('deposit'))['total_deposits']

                # Calculate total withdrawals
                withdrawals = UsersDepositsandWithdrawals.objects.aggregate(total_withdrawals=Sum('withdrawal'))['total_withdrawals']


                if total_balance is not None:
                    self.users_cash = total_balance
                    self.amount_won_by_users = amount_out
                    self.amount_lost_by_users = amount_in
                    self.total_deposits = deposits
                    self.total_withdrawals = withdrawals
                    self.total_cash = self.users_cash + self.float_cash
                    self.total_real = self.total_cash - self.users_cash - self.amount_won_by_users + self.amount_lost_by_users
                    self.profit_to_owner = self.total_real - self.float_cash
                    self.save()

         
            
            except IntegrityError as e:
                # Handle database-related exceptions, such as IntegrityError
                # For example, you can log the error or take appropriate action.
                print("IntegrityError:", str(e))

            except Exception as e:
                # Handle other unexpected exceptions
                print("An unexpected error occurred:", str(e))
        
class BettingWindow(models.Model):
    is_open = models.BooleanField(default=False)
    
class CashoutWindow(models.Model):
    is_open = models.BooleanField(default=False)

class Games(models.Model):
    game_id = models.CharField(max_length=200)
    group_name = models.CharField(max_length=200,default='')
    hash = models.CharField(max_length=255, unique=True) 
    server_seed = models.CharField(max_length=255, unique=True)
    salt = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    crash_point = models.CharField(max_length=255, default='')
    
    
class Clients(models.Model):
    channel_name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    
