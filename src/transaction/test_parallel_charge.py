import pytest
import logging
from django.db import transaction, connections

from accounts.models import User
from transaction.models import Wallet, NotProcessedCreditChargeRequest as Npreq, SellCredit as Screq
from .threads import ThreadGroup, ThreadQueue
from data import users_data, CHARGE_COUNT, random_charge, SELL_COUNT, random_sell, generate_rand_patterns, TRANSACTION_CHARGE, TRANSACTION_SELL, Pattern

from functools import reduce
from random import choice

logger = logging.getLogger(__name__)

counter = 1

@pytest.fixture
def wallets():
    wallets = []
    for user_data in users_data:
        user = User(**user_data)
        user.save()
        wlt = user.profile.wallet
        wallets.append(wlt)
    return wallets


def charge_wallet(wallet):
    with lock:
        Npreq.objects.create(wallet=wallet, amount=charge_amount).save()
        wallet.refresh_from_db()
    


@pytest.mark.django_db(transaction=True)
def test_concurrent_charge_requests(wallets):
    queue = ThreadQueue()
        
    transaction_str_class_map = {
        TRANSACTION_CHARGE: Npreq,
        TRANSACTION_SELL: Screq,
    }
    
    #threads target function
    def perform_transaction(klass, wlt, amount):
        _type = TRANSACTION_CHARGE if klass == Npreq else TRANSACTION_SELL
        obj = klass(wallet=wlt, amount=amount)
        global counter
        count = str(counter).zfill(len(str((CHARGE_COUNT + SELL_COUNT) * len(wallets))))
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
        return Pattern(wlt.id, _type, amount)
    
    for wlt in wallets:
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
    
    logger.info(40*"-")
    for wlt in wallets:
        expect = reduce(reduce_key, ThreadGroup.get_group(wlt.id).get_results(), 0)
        wlt.refresh_from_db()
        logger.info(f"{wlt.id} total charges = {wlt.total_processed_credit_charges()}")
        logger.info(f"{wlt.id} total sells = {wlt.total_selled_credits()}")
        logger.info("")
        logger.info(f"{wlt.id} expected overall data = {expect}")
        logger.info(f"{wlt.id} current credit = {wlt.credit}")
        logger.info(40*"-")
        assert wlt.check_turnover_correctness()
        assert wlt.credit == expect