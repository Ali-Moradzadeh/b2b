from django.db import models, transaction
from accounts.models import Profile
from .managers import CreditChargeRequestManager, ProcessedCreditChargeRequestManager, NotProcessedCreditChargeRequestManager, SellCreditManager
from utils.validators import positive_amount_validator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Wallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.PROTECT)
    credit = models.PositiveIntegerField()
    
    class Meta:
        ordering = ("pk", )

    def processed_credit_charge_requests(self):
        return self.credit_charge_requests.filter(processed=True)
    
    def total_processed_credit_charges(self):
        total = self.processed_credit_charge_requests().aggregate(models.Sum("amount")).get("amount__sum", 0)
        return total if total else 0
    
    def total_selled_credits(self):
        x = self.selled_credits.aggregate(models.Sum("amount")).get("amount__sum", 0)
        return x if x else 0
    
    def check_turnover_correctness(self):
        return self.credit + self.total_selled_credits() == self.total_processed_credit_charges()
    
    def __str__(self):
        return f"{self.profile}<{self.credit}>"


class CreditChargeRequest(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='credit_charge_requests', null=True)
    amount = models.PositiveIntegerField(validators=[positive_amount_validator])
    request_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(blank=True)
    
    objects = CreditChargeRequestManager()
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gt=0), name='positive_charge_amount'),
        ]
    
    def save(self, *args, **kwargs):
        if settings.AUTO_PROCESS_CHARGE_REQUESTS:
            self.processed=True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.wallet}<+{self.amount}>"


class NotProcessedCreditChargeRequest(CreditChargeRequest):
    
    objects = NotProcessedCreditChargeRequestManager()
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    class Meta:
        proxy = True

class ProcessedCreditChargeRequest(CreditChargeRequest):
    
    objects = ProcessedCreditChargeRequestManager()
    
    class Meta:
        proxy = True
    
    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        #avoid creating processed request directly.
        if not self.pk:
            raise ValidationError(_("Can't directly create a processed credit charge request"))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        self.processed = True
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"{self.wallet}<+={self.amount}>"


class SellCredit(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='selled_credits')
    amount = models.PositiveIntegerField(validators=[positive_amount_validator])
    request_date = models.DateTimeField(auto_now_add=True)
    
    #objects = SellCreditManager()
    
    def clean(self, *args, **kwargs):
        if self.amount > self.wallet.credit:
            raise ValidationError(_("not enough wallet credit to sell"))
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        super().full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.wallet}<-={self.amount}>"
