from celery import Celery
from .models import Wallet
from transaction.serializers import front_serializers as front_srz
from django.db.models import F
from .serializers import front_serializers as fr_srz


app = Celery('core', broker='amqp://guest@localhost//')

@app.task
def sell_task(user_id, data):
    srz_cls = fr_srz.CreateSellRequestSerializer
    srz = srz_cls(data=data, context={"user_id": user_id})
    srz.is_valid(raise_exception=True)
    value = data.get("amount", 0)
    if value:
        srz.save()
        Wallet.objects.filter(profile__user__id=user_id).update(credit=F("credit")-value)
    return True
