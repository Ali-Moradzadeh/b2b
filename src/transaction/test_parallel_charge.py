
import pytest
import logging
from django.db import transaction, connections, connection

from accounts.models import User
from transaction.models import Wallet, NotProcessedCreditChargeRequest as Npreq, SellCredit as Screq
from .processes import ProcessGroup, ProcessQueue
from data import users_data, CHARGE_COUNT, random_charge, SELL_COUNT, random_sell, generate_rand_patterns, TRANSACTION_CHARGE, TRANSACTION_SELL, Pattern

from functools import reduce
from random import choice
from multiprocessing import Process


logger = logging.getLogger(__name__)


@pytest.fixture
def wallets():
    wallets = []
    for user_data in users_data:
        user = User(**user_data)
        user.save()
        wlt = user.profile.wallet
        wallets.append(wlt)
    return wallets


@pytest.mark.django_db(transaction=True)
def test_concurrent_charge_requests(wallets, django_db_blocker):
    queue = ProcessQueue()
    
    transaction_str_class_map = {
        TRANSACTION_CHARGE: Npreq,
        TRANSACTION_SELL: Screq,
    }
    
    #processs target function
    def perform_transaction(klass, wlt, amount):
        _type = TRANSACTION_CHARGE if klass == Npreq else TRANSACTION_SELL
        obj = klass(wallet=wlt, amount=amount)
        
        result = None
        try:
            with transaction.atomic():
                wlt.refresh_from_db()
                obj.save()
                msg = f"SUCCESS {wlt.id}, {_type}, {amount}"
                result = Pattern(wlt.id, _type, amount)
        except:
            msg = f"FAILEDD {wlt.id}, {_type}, {amount}"
        finally:
            logger.info(msg)
        return result
    
    for wlt in wallets:
        pg = ProcessGroup(wlt.id, perform_transaction, django_db_blocker)
        rnd_ptrns = generate_rand_patterns(wlt.id)
        for rnd_ptrn in rnd_ptrns:
            klass = transaction_str_class_map[rnd_ptrn.type]
            queue.establish(pg, args=(klass, wlt, rnd_ptrn.amount))
    
    queue.start_join_all()
    connections["default"].close()
    
    for wlt in wallets:
        wlt.refresh_from_db()
        rslts = ProcessGroup.get_group(wlt.id).get_results()
        
        logger.info(40*"-")
        expect_charge = reduce(lambda num, ptrn: num + ptrn.amount, filter(lambda i: i.type == TRANSACTION_CHARGE, rslts), 0)
        overall_charge = wlt.total_processed_credit_charges()
        
        logger.info(f"{wlt.id} expect charges = {expect_charge}")
        logger.info(f"{wlt.id} total charges = {overall_charge}")
        assert overall_charge == expect_charge
        
        logger.info("")
        expect_sell = reduce(lambda num, ptrn: num + ptrn.amount, filter(lambda i: i.type == TRANSACTION_SELL, rslts), 0)
        overall_sell = wlt.total_selled_credits()
        
        logger.info(f"{wlt.id} expect sells = {expect_sell}")
        logger.info(f"{wlt.id} total sells = {overall_sell}")
        assert overall_sell == expect_sell
        
        logger.info("")
        logger.info(f"{wlt.id} expect credit = {expect_charge - expect_sell}")
        logger.info(f"{wlt.id} current credit = {wlt.credit}")
        assert wlt.credit == expect_charge - expect_sell
        assert wlt.check_turnover_correctness()
    
    

"""

# test_create_records.py

import pytest
from multiprocessing import Process

from accounts.models import User
from .models import SellCredit as Sc

import time
from data import users_data
from random import choice, randint
from django.db import transaction, connections


import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def wallets():
    wallets = []
    for user_data in users_data:
        user = User(**user_data)
        user.save()
        wlt = user.profile.wallet
        wlt.credit = 10000
        wlt.save()
        wallets.append(wlt)
    return wallets


def create_records(django_db_blocker, wlt, start, end):
    connections.close_all()
    with django_db_blocker.unblock():
        for i in range(start, end):
            try:
                Sc(wallet=wlt, amount=randint(2, 7)).save()
                logger.info("Success")
            except Exception as e:
                logger.info(e)



# Test function for multiprocessing
@pytest.mark.django_db(transaction=True)
def test_create_records_parallel(wallets, django_db_blocker):
    num_records = 8

    processes = []
    chunk_size = num_records // 8

    from concurrent.futures import ProcessPoolExecutor

    for i in range(0, num_records, chunk_size):
        start = i
        end = min(i + chunk_size, num_records)
        
        process = Process(target=create_records, args=(django_db_blocker, choice(wallets), start, end))
        processes.append(process)
        process.start()
    
    for prs in processes:
        prs.join()
"""