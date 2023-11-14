from celery import Celery, shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from accounts.models import Profile, Notification
from .serializers import front_serializers as fr_srz


app = Celery('core')

@shared_task
def sell_task(user_id, data):
    notify_func = async_to_sync(get_channel_layer().group_send)
    value = data.get("amount", 0)
    try:
        srz_cls = fr_srz.CreateSellRequestSerializer
        srz = srz_cls(data=data, context={"user_id": user_id})
        srz.is_valid(raise_exception=True)
        if value:
            srz.save()
            msg = f"selling {value} credit was successfull."
    except:
        msg = f"selling {value} credit FAILED."
    finally:
        profile = Profile.objects.get(user__id=user_id)
        Notification(profile=profile, message=msg).save()
        notify_func(f"user_{user_id}_transaction_notification", {"type": "notify"})
    