from django.core.management.base import BaseCommand
from region_app.models import Councils
from user.models import User
import os

class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        try:
            uk_postcodes = os.path.join(os.path.dirname(__file__), '../../uk_postcodes.txt')
            with open(uk_postcodes) as f:
                postcodes = f.read()
                admin_user = User.objects.get(email="burluudaysantoshkumar3@gmail.com")
                Councils.objects.create(
                    name="UK",
                    postcodes=postcodes,
                )
                

            self.stdout.write(self.style.SUCCESS("Completed processing"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
