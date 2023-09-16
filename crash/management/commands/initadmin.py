
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):

    def handle(self, *args, **options):
        print('reached here')
        
        User = get_user_model()

        # Define the user details
        user_name = 'admin'
        phone_number = '0714313598'
        password = 'admin'

        if not User.objects.filter(phone_number=phone_number).exists():
            print("let's go")
            print('Creating account for %s (%s)' % (user_name, phone_number))
            admin = User.objects.create_superuser(
                phone_number=phone_number, user_name=user_name, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.is_staff = True
            admin.save()
        else:
            print('User with phone number %s already exists' % phone_number)
