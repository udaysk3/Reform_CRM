from django.core.management.base import BaseCommand
from home.models import Cities
from datetime import datetime
from user.models import User
import pytz
import os
import pandas as pd


class Command(BaseCommand):
    help = 'Create cities only once'
    def handle(self, *args, **options):
        csv_filename = os.path.join(os.path.dirname(__file__), '../../cities.csv')
        data = pd.read_csv(csv_filename)
        cities = data['City/Town/Village'].tolist()
        if Cities.objects.exists():
            self.stdout.write(self.style.SUCCESS('Objects already exist. No action taken.'))
        else:
            for city in cities:
                if not Cities.objects.filter(name=city).exists():
                    Cities.objects.create(name=city, created_at=datetime.now(pytz.timezone('Europe/London')), agent=User.objects.get(email="admin@gmail.com"))
            self.stdout.write(self.style.SUCCESS('Objects created successfully.'))


