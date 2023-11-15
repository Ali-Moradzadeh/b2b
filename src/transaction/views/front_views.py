import logging

from django.db import transaction

from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from transaction.models import Wallet, NotProcessedCreditChargeRequest as Npreq
from transaction.serializers import front_serializers as front_srz
from transaction.tasks import sell_task

from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view


logger = logging.getLogger(__name__)


class CreateCreditChargeRequest(CreateAPIView):
    serializer_class = front_srz.CreateCreditChargeRequestSerializer
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request):
        try:
            data = request.data.get('amount')
            result = super().post(request)
        except Exception as e:
            logger.error(f"charging of {request.user} by {data} has error {e}")
            raise
        else:
            logger.info(f"{request.user.email} charge his wallet by {data}")
            return result


@api_view(http_method_names=['POST'])
def sell_credit(request):
    sell_task.delay(request.user.id, request.data)
    return Response({}, 201)