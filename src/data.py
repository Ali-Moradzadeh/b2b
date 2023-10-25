from django.contrib.auth.hashers import make_password
from collections import namedtuple
from django.urls import reverse


user_A = "a@gmail.com"
user_B = "b@gmail.com"
user_C = "c@gmail.com"
user_D = "d@gmail.com"
user_E = "e@gmail.com"
user_F = "f@gmail.com"


charge_url = reverse("create_credit_charge")
sell_url = reverse("sell_credit")


users_data = [
    {
        "email": user_A,
        "phone_number": "+989121235559",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
    {
        "email": user_B,
        "phone_number": "+989121235558",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
    {
        "email": user_C,
        "phone_number": "+989121235557",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
    {
        "email": user_D,
        "phone_number": "+989121235556",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
    {
        "email": user_E,
        "phone_number": "+989121235555",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
    {
        "email": user_F,
        "phone_number": "+989121235554",
        "password": make_password("adminPass?"),
        #"confrm_password": "adminPass?",
        "is_verified": True,
    },
]


pattern = namedtuple("Pattern", ["user", "url", "amount"])

user_A_transactions = [
    pattern(user_A, sell_url, 180),
    pattern(user_A, charge_url, 200),
    pattern(user_A, charge_url, 130),
    pattern(user_A, sell_url, 180),
]

user_B_transactions = [
    pattern(user_B, charge_url, 100),
    pattern(user_B, sell_url, 53),
    pattern(user_B, sell_url, 12),
    pattern(user_B, charge_url, 36),
    pattern(user_B, charge_url, 20),
    pattern(user_B, sell_url, 60),
]

user_C_transactions = [
    pattern(user_C, charge_url, 80),
    pattern(user_C, sell_url, 34),
    pattern(user_C, charge_url, 67),
    pattern(user_C, sell_url, 12),
    pattern(user_C, charge_url, 180),
    pattern(user_C, sell_url, 84),
]

user_D_transactions = [
    pattern(user_D, charge_url, 461),
    pattern(user_D, sell_url, 164),
    pattern(user_D, sell_url, 231),
    pattern(user_D, sell_url, 40),
]

user_E_transactions = [
    pattern(user_E, charge_url, 80),
    pattern(user_E, sell_url, 56),
    pattern(user_E, sell_url, 13),
    pattern(user_E, charge_url, 40),
    pattern(user_E, sell_url, 43),
]

user_F_transactions = [
    pattern(user_F, charge_url, 45),
    pattern(user_F, charge_url, 36),
    pattern(user_F, sell_url, 67),
    pattern(user_F, sell_url, 12),
    pattern(user_F, charge_url, 73),
    pattern(user_F, sell_url, 49),
]


transaction_patterns = user_A_transactions + user_B_transactions + user_C_transactions + user_D_transactions + user_E_transactions + user_F_transactions