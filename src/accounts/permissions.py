from rest_framework.permissions import BasePermission
from .models import User


class ActiveOwner(BasePermission):
    def has_object_permission(self, request, view, instance):
        #return True
        return request.user.is_authenticated and request.user.is_active and view.get_owner(request) == instance