from django.test import TestCase, Client, TransactionTestCase
from django.conf import settings
from accounts.models import User
from transaction.models import NotProcessedCreditChargeRequest as Npreq, SellCredit as Screq, Wallet
from django.urls import reverse
from django.test import override_settings
from data import users_data, CHARGE_COUNT, random_charge, SELL_COUNT, random_sell, generate_rand_patterns, TRANSACTION_CHARGE, TRANSACTION_SELL, Pattern

from random import choice
from django.db import transaction
from .threads import ThreadGroup, ThreadQueue
from functools import reduce
import logging
from django.db import connections


logger = logging.getLogger(__name__)


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
        l = len(self.wallets)
        for i in range(CHARGE_COUNT*l):
            wlt = self.wallets[i%l]
            Npreq(wallet=wlt, amount=random_charge()).save()
            wlt.refresh_from_db()
        
        for wallet in self.wallets:
            print(f"{wallet} overall charges is {wallet.total_processed_credit_charges()}")
        
        
        rand_sells = [Screq(wallet=choice(self.wallets), amount=random_sell()) for _ in range(SELL_COUNT)]
        
        for sell in rand_sells:
            try:
                with transaction.atomic():
                    sell.save()
            except Exception as e:
                pass
                #print(e)
                
        for wallet in self.wallets:
            wallet.refresh_from_db()
            print(f"{wallet} overall sells is {wallet.total_selled_credits()}")
        
        for wallet in self.wallets:
            b = wallet.check_turnover_correctness()
            print(f"{wallet} turnover is {b}")
            self.assertTrue(b)
    
    def test_parallel_transaction(self):
        queue = ThreadQueue()
        
        transaction_str_class_map = {
            TRANSACTION_CHARGE: Npreq,
            TRANSACTION_SELL: Screq,
        }
        
        #threads target function
        def perform_transaction(klass, wlt, amount):
            obj = klass(wallet=wlt, amount=amount)
            count = str(counter).zfill(len(str(CHARGE_COUNT + SELL_COUNT))
            counter += 1
            try:
                with transaction.atomic():
                    obj.save()
                    wlt.refresh_from_db()
                    msg = f"{count} SUCCESS {wlt.id}, {klass.__name__}, {amount}"
            except Exception as e:
                msg = f"{count} FAILED {wlt.id}{klass.__name__} {amount}"
            finally:
                logger.info(msg)
                
                connections["default"].close()
            _type = TRANSACTION_CHARGE if klass == Npreq else TRANSACTION_SELL
            return Pattern(wlt.id, _type, amount)
        
        for wlt in self.wallets:
            tg = ThreadGroup(wlt.id, perform_transaction)
            rnd_ptrns = generate_rand_patterns(wlt.id)
            for rnd_ptrn in rnd_ptrns:
                klass = transaction_str_class_map[rnd_ptrn.type]
                queue.establish(tg, args=(klass, wlt, rnd_ptrn.amount))
        
        queue.start_join_all(100)
        
        def reduce_key(pre, result_item):
            amount = result_item.amount
            if result_item.type == TRANSACTION_CHARGE:
                return pre + amount
            elif pre >= amount:
                return pre - amount
            else:
                return pre
        
        print(40*"-")
        for wlt in self.wallets:
            expect = reduce(reduce_key, ThreadGroup.get_group(wlt.id).get_results(), 0)
            wlt.refresh_from_db()
            logger.info(f"{wlt.id} total charges = {wlt.total_processed_credit_charges()}")
            logger.info(f"{wlt.id} total sells = {wlt.total_selled_credits()}")
            print("")
            logger.info(f"{wlt.id} expected overall data = {expect}")
            logger.info(f"{wlt.id} current credit = {wlt.credit}")
            print(40*"-")
            self.assertTrue(wlt.check_turnover_correctness())
            self.assertEqual(wlt.credit, expect)
    