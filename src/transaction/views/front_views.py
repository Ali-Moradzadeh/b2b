from rest_framework.generics import CreateAPIView
from transaction.serializers import front_serializers as front_srz
from transaction.models import CreditChargeRequest
from django.db import transaction
import logging


logger = logging.getLogger(__name__)

class CreateCreditChargeRequest(CreateAPIView):
    serializer_class = front_srz.CreateCreditChargeRequestSerializer
    
    @transaction.atomic
    def post(self, request):
        try:
            result = super().post(request)
        except Exception as e:
            logger.error(f"charging of {request.user} has error {e}")
            raise
        else:
            logger.info(f"{request.user.email} charge his wallet")
            return result


class CreateSellCreditRequest(CreateAPIView):
    serializer_class = front_srz.CreateSellRequestSerializer
    
    @transaction.atomic
    def post(self, request):
        try:
            result = super().post(request)
        except Exception as e:
            logger.error(f"sell credit of {request.user} has error")
            raise
        else:
            logger.info(f"{request.user.email} sell credit")
            return result