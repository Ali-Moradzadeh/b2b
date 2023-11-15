import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from locust import HttpUser, task, constant
from django.urls import reverse
from rest_framework.authtoken.models import Token
from accounts.models import User
from random import randint


#test_users = list(User.objects.filter(email__startswith="test_user").order_by('id').values_list("id", flat=True))

tokens = list(Token.objects.exclude(user__id=1).order_by('user__id')[:])

charge_url = reverse('credit_charge')
sell_url = reverse('sell_credit')
urls = (charge_url, sell_url)


class PostApiUser(HttpUser):
    host = "http://127.0.0.1:8000"
    user_id = 0
    wait_time = constant(1)
    
    def on_start(self):
        token = tokens[self.__class__.user_id]
        self.__class__.user_id += 1
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {token.key}'
        }
    
    def on_stop(self):
        super().on_stop()
        self.__class__.user_id = 0
    
    #@task
    def buy_credit(self):
        self.client.post(charge_url, json={'amount': randint(10, 50)}, headers=self.headers)
    
    @task
    def sell_credit(self):
        self.client.post(sell_url, json={'amount': randint(1, 10)}, headers=self.headers)
    