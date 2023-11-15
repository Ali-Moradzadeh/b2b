import logging

from django.db import transaction

from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from transaction.models import Wallet, NotProcessedCreditChargeRequest as Npreq
from transaction.serializers import front_serializers as front_srz
from transaction.tasks import sell_task
from rest_framework.decorators import api_view, permission_classes


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
@permission_classes([IsAuthenticated, ])
def background_sell_credit(request):
    sell_task.delay(request.user.id, request.data)
    return Response({"status", "processing"}, 201)


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated, ])
def sell_credit(request):
    return Response({"status": "created"}, 201)