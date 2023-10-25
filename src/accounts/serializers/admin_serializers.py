from accounts.models import User
from rest_framework import serializers, status
from rest_framework.response import Response


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'password', 'is_staff', 'is_superuser', 'is_active')


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
	
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'password', 'confirm_password', 'is_staff', 'is_superuser', 'is_active')
        extra_kwargs = {'is_active': {'default': True}}
            
    
    def validate(self, data):
        if data["confirm_password"] != data["password"]:
            raise serializers.ValidationError("password and its confirm must be exactly same")
        return data

    def create(self, validated_data):
    	instance = User.objects.create_user(**validated_data)
    	return self.__class__(instance).data


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'is_staff', 'is_superuser', 'is_active')


class ChangeUserPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
	
    class Meta:
        model = User
        fields = ('new_password', 'confirm_new_password')
    
    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("new password and its confirm must be exactly same.")
        return data
    
    def save(self):
        super().save()
        self.instance.set_password(self.validated_data['new_password'])
        self.instance.save()
        return self.instance

