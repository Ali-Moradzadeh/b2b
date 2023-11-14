from django.urls import path
from .consumers import NotificationConsumer

urlpatterns = [
    path("ws/transaction/notification/$", NotificationConsumer.as_asgi()),
]
