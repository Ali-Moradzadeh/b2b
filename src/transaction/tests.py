from django.test import TestCase, Client, TransactionTestCase
from django.conf import settings
from accounts.models import User
from transaction.models import NotProcessedCreditChargeRequest as Npreq, SellCredit as Screq, Wallet
from django.urls import reverse
from django.test import override_settings
from data import users_data, CHARGE_COUNT, SELL_COUNT, TRANSACTION_CHARGE, TRANSACTION_SELL, Pattern, transaction_str_class_map, generate_rand_patterns

from random import choice
from django.db import transaction
from .threads import ThreadGroup, ThreadQueue
from functools import reduce
import logging
from django.db import connections


logger = logging.getLogger(__name__)

counter = 1

@override_settings(SIGNALS=True)
class TransactionTest(TransactionTestCase):
    
    def setUp(self):
        self.wallets = []
        for user_data in users_data:
            user = User(**user_data)
            user.save()
            wlt = user.profile.wallet
            self.wallets.append(wlt)
    
    def test_turnover(self):
        def perform_transaction(klass, wlt, amount):
            _type = TRANSACTION_CHARGE if klass == Npreq else TRANSACTION_SELL
            obj = klass(wallet=wlt, amount=amount)
            global counter
            count = str(counter).zfill(len(str((CHARGE_COUNT + SELL_COUNT) * len(self.wallets))))
            counter += 1
            try:
                with transaction.atomic():
                    obj.save()
                    wlt.refresh_from_db()
                    msg = f"{count} SUCCESS {wlt.id}, {_type}, {amount}"
            except Exception as e:
                msg = f"{count} FAILEDD {wlt.id} {_type} {amount}"
            finally:
                logger.info(msg)
                connections["default"].close()
    
        for wlt in self.wallets:
            rnd_ptrns = generate_rand_patterns(wlt.id)
            for rnd_ptrn in rnd_ptrns:
                klass = transaction_str_class_map[rnd_ptrn.type]
                perform_transaction(klass, wlt, rnd_ptrn.amount)
        
        for wallet in self.wallets:
            logger.info(f"{wallet} overall charges is {wallet.total_processed_credit_charges()}")
        
        for wallet in self.wallets:
            b = wallet.check_turnover_correctness()
            logger.info(f"{wallet} turnover is {b}")
            self.assertTrue(b)
   