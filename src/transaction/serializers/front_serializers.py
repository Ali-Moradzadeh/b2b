from rest_framework import serializers
from transaction.models import NotProcessedCreditChargeRequest as Npreq, SellCredit, Wallet
from django.db import transaction


class CreateCreditChargeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Npreq
        fields = ("amount", )
    
    def validate(self, data):
        data = super().validate(data)
        data['wallet'] = self.context['request'].user.profile.wallet
        return data

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class CreateSellRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellCredit
        fields = ("amount", )
    
    def validate(self, data):
        data = super().validate(data)
        data['wallet'] = self.context['request'].user.profile.wallet
        return data

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    