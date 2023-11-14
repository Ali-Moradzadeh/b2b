from .models import Wallet, NotProcessedCreditChargeRequest as Npreq, SellCredit
from accounts.models import Profile
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models import F


@receiver(post_save, sender=Profile)
def auto_create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(profile=instance, credit=0)

@receiver(post_save, sender=Npreq)
def charge_credit(sender, instance, created, **kwargs):
    if instance.processed:
        Wallet.objects.filter(profile=instance.wallet.profile).update(credit=F("credit")+instance.amount)


@receiver(post_save, sender=SellCredit)
def sell_credit(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.filter(profile=instance.wallet.profile).update(credit=F("credit")-instance.amount)