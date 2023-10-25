from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager, InactiveUserManager, StaffManager, CustomerManager
from utils.validators import username_validator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if self.is_superuser or self.is_staff:
            self.is_verified = True
        super().save(*args, **kwargs)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    
    def __str__(self):
        return self.email
    
        
    @property
    def can_authenticate(self):
        return self.is_active and self.is_verified


class StaffUser(User):
    objects = StaffManager()
    
    class Meta:
        proxy = True


class CustomerUser(User):
    objects = CustomerManager()
    
    class Meta:
        proxy = True
    

class InactiveUser(User):
    objects = InactiveUserManager()
    
    class Meta:
        proxy = True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True, validators=[username_validator], null=True, blank=True)
    bio = models.TextField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username if self.username else self.user.email
