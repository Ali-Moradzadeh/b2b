from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from accounts.models import User, Profile
from accounts.serializers import front_serializers as front_srz
from accounts.permissions import ActiveOwner
from django.core.exceptions import PermissionDenied


class CreateUserAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [ActiveOwner]
    
    def get_owner(self, request):
        return request.user
    
    def get_permissions(self):
        match self.action:
            case 'list':
                raise PermissionDenied()
            case _:
                return [permission() for permission in self.permission_classes]
    
    def get_serializer_class(self):
        match self.action:
            case 'retrieve':
                return front_srz.RetrieveUserSerializer
            case 'create':
                return front_srz.CreateUserSerializer
            case 'update':
                return front_srz.UpdateUserSerializer
            case 'partial_update':
                return front_srz.UpdateUserSerializer
            case 'change_password':
                return front_srz.ChangeUserPasswordSerializer
            case _:
                return front_srz.RetrieveUserSerializer
    
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
        return Response({"deleted": "Done."}, status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [ActiveOwner]
    
    def get_owner(self, request):
        return request.user.profile
    
    def get_permissions(self):
        match self.action:
            case 'list':
                raise PermissionDenied()
            case _:
                return [permission() for permission in self.permission_classes]
    
    def get_serializer_class(self):
        match self.action:
            case 'retrieve':
                return front_srz.RetrieveProfileSerializer
            case 'create':
                return front_srz.CreateUserSerializer
            case 'update':
                return front_srz.RetrieveProfileSerializer
            case 'partial_update':
                return front_srz.RetrieveProfileSerializer
            case _:
                return front_srz.RetrieveUserSerializer
        
        def destroy(self, request, pk):
            instance = Profile.objects.get(pk=pk)
            instance.is_deleted = True
            instance.save()
            return Response({"deleted": "Done."}, status=status.HTTP_204_NO_CONTENT)