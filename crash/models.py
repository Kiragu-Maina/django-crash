from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
import re
phone_validator = RegexValidator(r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$", "The phone number provided is invalid")



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
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    # is_translator = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_name

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value



class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.IntegerField()
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    won = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.user)

