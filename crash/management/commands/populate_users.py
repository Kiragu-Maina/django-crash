import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from faker import Faker
from ...models import User

fake = Faker()

class Command(BaseCommand):
    help = 'Run the GameManager in the background'

    def handle(self, *args, **kwargs):
        
        def generate_user_data(num_users):
            users = []
            for _ in range(num_users):
                # Generate a 10-digit phone number starting with "01" or "07"
                phone_number = fake.random_element(elements=('01', '07')) + str(fake.random_number(digits=8))
                user_name = fake.unique.user_name()
                password = fake.password()
                user_to_json = {
                    'phone_number': phone_number,
                    'user_name': user_name,
                    'password': password,
                }
               
                user = User.objects.create(phone_number=phone_number, user_name=user_name)
                user.set_password(password)
                user.save()
                users.append(user_to_json)
            file_path = os.path.join(settings.MEDIA_ROOT, 'users.json')

            with open(file_path, 'w') as json_file:
                json.dump(users, json_file)
                print('users generated')

        num_users = 300
        generate_user_data(num_users)
