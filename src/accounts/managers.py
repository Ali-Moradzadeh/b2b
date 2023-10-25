from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager, QuerySet, Q


staff_q = Q(is_superuser=True) | Q(is_staff=True)

class ActiveUserQueryset(QuerySet):
    def delete(self):
        return self.update(is_active=Q(is_active=False))


class UserManager(BaseUserManager):
    def get_queryset(self):
        return ActiveUserQueryset(self.model, self._db).filter(is_active=True)
    
    
    def create_user(self, email, phone_number, password, confirm_password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        if password != confirm_password:
            raise ValueError('passwords must be exactly the same')
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password, confirm_password, **extra_fields):
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, phone_number, password, confirm_password, **extra_fields)


class InactiveUserManager(Manager):
    def get_queryset(self):
        return ActiveUserQueryset(self.model, self._db).filter(is_active=False)


class StaffManager(Manager):
    def get_queryset(self):
        return ActiveUserQueryset(self.model, self._db).filter(Q(is_active=True) & staff_q)

    
class CustomerManager(Manager):
    def get_queryset(self):
        return ActiveUserQueryset(self.model, self._db).filter(Q(is_active=True) & ~staff_q)
