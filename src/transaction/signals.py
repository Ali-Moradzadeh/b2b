from .models import Wallet, NotProcessedCreditChargeRequest, SellCredit
from accounts.models import Profile
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver(post_save, sender=Profile)
def auto_create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(profile=instance, credit=0)

@receiver(post_save, sender=NotProcessedCreditChargeRequest)
def charge_credit(sender, instance, created, **kwargs):
    if instance.processed:
        instance.wallet.credit += instance.amount
        instance.wallet.save()


@receiver(post_save, sender=SellCredit)
def sell_credit(sender, instance, created, **kwargs):
    if created:
        
        instance.wallet.credit -= instance.amount
        instance.wallet.save()