from django.core.management.base import BaseCommand
from home.models import Councils
from home.councils import councils
from datetime import datetime
from user.models import User
import pytz

class Command(BaseCommand):
    help = 'Create councils only once'
    def handle(self, *args, **options):
        if Councils.objects.exists():
            self.stdout.write(self.style.SUCCESS('Objects already exist. No action taken.'))
        else:
            for council in councils:
                if not Councils.objects.filter(name=council['title']).exists():
                    Councils.objects.create(name=council['title'], created_at=datetime.now(pytz.timezone('Europe/London')), agent=User.objects.get(email="admin@gmail.com"))
            self.stdout.write(self.style.SUCCESS('Objects created successfully.'))
