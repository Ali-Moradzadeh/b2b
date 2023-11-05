from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from transaction.serializers import front_serializers as front_srz
from transaction.models import CreditChargeRequest
from django.db import transaction
from transaction.models import Wallet,  NotProcessedCreditChargeRequest as Npreq
import logging


logger = logging.getLogger(__name__)


class CreateCreditChargeRequest(CreateAPIView):
    serializer_class = front_srz.CreateCreditChargeRequestSerializer


class CreateSellCreditRequest(CreateAPIView):
    serializer_class = front_srz.CreateSellRequestSerializer