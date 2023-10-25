from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from accounts.serializers import admin_serializers as admin_srz
from accounts.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        match self.action:
            case 'list':
                return admin_srz.ListUserSerializer
            case 'retrieve':
                return admin_srz.ListUserSerializer
            case 'create':
                return admin_srz.CreateUserSerializer
            case 'update':
                return admin_srz.UpdateUserSerializer
            case 'partial_update':
                return admin_srz.UpdateUserSerializer
            case 'change_password':
                return admin_srz.ChangeUserPasswordSerializer
    
    @action(detail=True, methods=['patch'])
    def change_password(self, request, pk):
        instance = User.objects.get(pk=pk)
        srz = self.get_serializer_class()(instance=instance, data=request.data)
        if srz.is_valid():
            srz.save()
            return Response(srz.data, status=status.HTTP_200_OK)
        return Response(srz.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk):
        instance = User.objects.get(pk=pk)
        instance.is_active = False
        instance.save()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
