from django.contrib.auth.hashers import make_password
from collections import namedtuple
from django.urls import reverse
from random import randint, choice
from transaction.models import Wallet, NotProcessedCreditChargeRequest as Npreq, SellCredit as Screq

USERS_COUNT = 3

TRANSACTION_CHARGE = "charge"
TRANSACTION_SELL = "sell"

CHARGE_RANGE = (10000, 100000)
SELL_RANGE = (100, 1000)

CHARGE_COUNT = 10
SELL_COUNT = 10

random_charge = lambda: randint(*CHARGE_RANGE)
random_sell = lambda: randint(*SELL_RANGE)

TRANSACTION_TYPES = ("charge", "sell")

TRANSACTION_AMOUNT_RAND_GENERATOR = {
    TRANSACTION_CHARGE: random_charge,
    TRANSACTION_SELL: random_sell
}

transaction_str_class_map = {
    TRANSACTION_CHARGE: Npreq,
    TRANSACTION_SELL: Screq, 
}

transactions_map = CHARGE_COUNT * [TRANSACTION_CHARGE] + SELL_COUNT * [TRANSACTION_SELL]


charge_url = reverse("credit_charge")
sell_url = reverse("sell_credit")

user_email_creator = lambda n: f"test_user_{n}@gmail.com"
phone_number_creator = lambda n: "+98917123" + "{:04d}".format(n)


users_data = []

for i in range(1, USERS_COUNT+1):
    predefined_user_data = {
        "email" : user_email_creator(i),
        "phone_number": phone_number_creator(i),
        "password": make_password("adminPass?"),
        "is_verified": True,
    }
    users_data.append(predefined_user_data)

Pattern = namedtuple("Pattern", ["wallet_id", "type", "amount"])

def generate_rand_patterns(wallet_id):
    tm_clone = transactions_map[::]
    patterns = []
    while tm_clone:
        transaction_type = choice(tm_clone)
        tm_clone.remove(transaction_type)
        rand_data = TRANSACTION_AMOUNT_RAND_GENERATOR[transaction_type]()
        
        ptrn = Pattern(wallet_id, transaction_type, rand_data)
        patterns.append(ptrn)
    return patterns