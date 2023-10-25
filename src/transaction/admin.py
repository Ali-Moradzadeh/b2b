from django.contrib import admin
from .models import Wallet, CreditChargeRequest, ProcessedCreditChargeRequest, NotProcessedCreditChargeRequest, SellCredit
from django.db import transaction
from django.db.models import Sum, F


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("profile", "credit")

class CreditChargeRequestAdmin(admin.ModelAdmin):
    list_display = ("get_username", "amount", "processed")
    list_filter = ("processed", )
    
    def get_username(self, instance):
        return instance.wallet.profile
    get_username.short_description = "username"


admin.site.register(ProcessedCreditChargeRequest, CreditChargeRequestAdmin)
admin.site.register(NotProcessedCreditChargeRequest, CreditChargeRequestAdmin)

@admin.register(SellCredit)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount")
