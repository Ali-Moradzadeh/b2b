from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import front_views
from accounts.views import admin_views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

router = DefaultRouter()
router.register(r'front-users', front_views.UserViewSet, basename='users')
router.register(r'front-profiles', front_views.ProfileViewSet, basename='profiles')
router.register(r'admin-users', admin_views.UserViewSet, basename='admin')

front_urls = []
front_urls += router.urls


urlpatterns = [
    path('api-token-auth/', front_views.CreateUserAuthTokenView.as_view()),
    path('', include('rest_framework.urls')),
    path('reset-password/', PasswordResetView.as_view(), name='password_reset'),
    path('reset-password-sent/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password-complete/', PasswordResetCompleteView.as_view(), name='password_reset_done'),
    ]

urlpatterns += front_urls
