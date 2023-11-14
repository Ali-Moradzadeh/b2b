from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transaction.views import front_views
from django.db import transaction


front_urls = [
    path("create-credit-charge-request/", front_views.CreateCreditChargeRequest.as_view(), name="credit_charge"),
    path("create-sell-credit/", front_views.CreateSellCreditRequest.as_view(), name="sell_credit"),
]


urlpatterns = []

urlpatterns += front_urls
