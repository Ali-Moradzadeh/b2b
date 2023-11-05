import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

clear = lambda: os.system("clear")

from transaction.models import (Wallet, ProcessedCreditChargeRequest as Preq,
    NotProcessedCreditChargeRequest as Npreq, SellCredit)
from django.db.models import Sum


def getwallet(id):
    return Wallet.objects.get(id=id)

def aggregateof(klass, obj):
    d = klass.objects.filter(wallet=obj).aggregate(Sum("amount")).get("amount__sum", 0)
    
    return d if d else 0


def detail(obj):
    x = getwallet(obj)
    s = aggregateof(SellCredit, x)
    p = aggregateof(Preq, x)
    
    print("Charges:", p)
    print("Sells:", s)
    print("now:", x.credit)
    print("validation:", x.check_turnover_correctness())
    print()


def delcharges():
    for c in Preq.objects.all():
        c.delete()

def delsells():
    for s in SellCredit.objects.all():
        s.delete()

def addcharge(amount):
    wlts = Wallet.objects.all()[:]
    for i in range(1, 31):
        Npreq.objects.create(wallet=wlts[i], amount=amount)

def setzero():
    Wallet.objects.update(credit=0)
    delcharges()
    delsells()