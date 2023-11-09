from django.core.management.base import BaseCommand,CommandError
from accounts.models import User


count = 200

class Command(BaseCommand):
    help='create test users for request load test'

    def handle(self,*args,**kwargs):
        for i in range(51, count+1):
            if i < 10:
                email = f"test_user_0{i}@gmail.com"
                phone = f"+98917165120{i}"
            else:
                email = f"test_user_{i}@gmail.com"
                phone = f"+9891716512{i}"
            
            password = "Pass123?"
            
            data = {
                "email": email,
                "phone_number": phone,
                "password": password,
                "confirm_password": password,
                "is_verified": True,
            }
            
            User.objects.create_user(**data)
        self.stdout.write(f"Successfully Created {count} test users")