import pytest
from django.test import TestCase, Client
from accounts.models import User
from transaction.models import ProcessedCreditChargeRequest as Npreq, Wallet
import threading
from functools import partial
from django.urls import reverse
from django.test import override_settings
from data import users_data, transaction_patterns


@override_settings(SIGNALS=True)
class TransactionTest(TestCase):
    
    def setUp(self):
        self.users = {}
        for user_data in users_data:
            user = User(**user_data)
            user.save()
            self.users[user_data["email"]] = user
        self.client = Client()
    
    def test_pattern(self):
        
        for tp in transaction_patterns:
            data = {"amount": tp.amount}
            
            self.client.login(username=tp.user, password='adminPass?')

            srz = self.client.post(tp.url, data)
            user = self.users[tp.user]
            
            correctness = Wallet.objects.get(profile__user=user).check_turnover_correctness()
            self.assertTrue(correctness)