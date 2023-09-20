import os
import json
from django.core.management.base import BaseCommand
import random
from faker import Faker

fake = Faker()
from ...models import User
class Command(BaseCommand):
    help = 'Run the GameManager in the background'

    def handle(self, *args, **kwargs):
        
        def generate_user_data(num_users):
            users = []
            for _ in range(num_users):
                phone_number = fake.unique.phone_number()
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

            with open('users.json', 'w') as json_file:
                json.dump(users, json_file)
        num_users = 300
        generate_user_data(num_users)

