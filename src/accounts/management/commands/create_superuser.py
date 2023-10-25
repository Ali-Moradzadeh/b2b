from django.core.management.base import BaseCommand,CommandError
from accounts.models import User


class Command(BaseCommand):
    help='create superuser for admin panel full control'

    def handle(self,*args,**kwargs):
        data = {
            "email": "admin@gmail.com",
            "phone_number": "+989123456789",
            "password": "adminPass?",
            "confirm_password": "adminPass?",
        }
        User.objects.create_superuser(**data)
        self.stdout.write(f"Successfully Created")