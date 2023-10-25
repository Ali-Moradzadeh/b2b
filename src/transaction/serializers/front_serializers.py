from rest_framework import serializers
from transaction.models import NotProcessedCreditChargeRequest as Npreq, SellCredit


class CreateCreditChargeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Npreq
        fields = ("amount", )
    
    def validate(self, data):
        data = super().validate(data)
        data['wallet'] = self.context['request'].user.profile.wallet
        return data


class CreateSellRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellCredit
        fields = ("amount", )
    
    def validate(self, data):
        data = super().validate(data)
        data['wallet'] = self.context['request'].user.profile.wallet
        return data

    def save(self, *args, **kwargs):
        try:
            instance = SellCredit(**self.validated_data)
            instance.full_clean()
            return super().save(*args, **kwargs)
        except Exception as e:
            raise serializers.ValidationError(e)
    