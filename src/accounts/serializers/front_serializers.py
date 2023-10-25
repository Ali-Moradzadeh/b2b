from accounts.models import User, Profile
from rest_framework import serializers, status
from rest_framework.response import Response


class RetrieveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone_number', )


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
	
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password', 'confirm_password')
    
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
        fields = ('email', 'phone_number')


class ChangeUserPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
	
    class Meta:
        model = User
        fields = ('password', 'new_password', 'confirm_new_password')
    
    def validate_password(self, password):
        if self.instance.check_password(password):
            return password
        raise serializers.ValidationError("Password Incorrect!")
        
    
    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("new password and its confirm must be exactly same.")
        return data
    
    def save(self):
        super().save()
        self.instance.set_password(self.validated_data['new_password'])
        self.instance.save()
        return self.instance


class RetrieveProfileSerializer(serializers.ModelSerializer):
    
    user = serializers.SerializerMethodField()
    
    
    def get_user(self, instance):
        return RetrieveUserSerializer(instance=instance.user).data
    
    class Meta:
        model = Profile
        fields = ( 'user', 'name', 'username', 'bio', 'profile_picture', 'gender')