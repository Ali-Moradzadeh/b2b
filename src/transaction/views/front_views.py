from rest_framework.generics import CreateAPIView
from transaction.serializers import front_serializers as front_srz
from rest_framework.permissions import IsAuthenticated
from transaction.models import Wallet
from transaction.models import CreditChargeRequest
from django.db import transaction
import logging


logger = logging.getLogger(__name__)

class CreateCreditChargeRequest(CreateAPIView):
    serializer_class = front_srz.CreateCreditChargeRequestSerializer
    permission_classes = [IsAuthenticated, ]
    
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data.get('amount')
            Wallet.objects.select_for_update().get(profile__user__id=request.user.id)
            result = super().post(request)
        except Exception as e:
            logger.error(f"charging of {request.user} by {data} has error {e}")
            raise
        else:
            logger.info(f"{request.user.email} charge his wallet by {data}")
            return result


class CreateSellCreditRequest(CreateAPIView):
    serializer_class = front_srz.CreateSellRequestSerializer
    permission_classes = [IsAuthenticated, ]
    
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data.get('amount')
            Wallet.objects.select_for_update().get(profile__user__id=request.user.id)
            result = super().post(request)
        except Exception as e:
            logger.error(f"{request.user} selling credit by {data} has error")
            raise
        else:
            logger.info(f"{request.user.email} sell {data} credit")
            return result