from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import SessionAuthentication as SessionAuth, TokenAuthentication as TokenAuth
from django.utils.translation import gettext_lazy as _


class SessionAuthentication(SessionAuth):
    def authenticate(self, request):
        sup = super().authenticate(request)
        if sup is None:
            return sup
        user = sup[0]
        if not user.is_verified:
            msg = _("your account has not been verified yet.")
            raise AuthenticationFailed(msg)
        return sup


class TokenAuthentication(TokenAuth):
    def authenticate(self, request):
        sup = super().authenticate(request)
        if sup is None:
            return None
        user = sup[0]
        if not user.is_verified:
            msg = _("your account has not been verified.")
            raise AuthenticationFailed(msg)
        return sup