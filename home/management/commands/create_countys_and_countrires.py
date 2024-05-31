from django.core.management.base import BaseCommand
from home.models import Countys, Countries
from datetime import datetime
from user.models import User
import pytz
import os
import pandas as pd


class Command(BaseCommand):
    help = 'Create countys only once'
    def handle(self, *args, **options):
        countys = [
  "Aberdeenshire",
  "Anglesey",
  "Angus (Forfarshire)",
  "Antrim",
  "Argyllshire",
  "Armagh",
  "Ayrshire",
  "Banffshire",
  "Bedfordshire",
  "Berkshire",
  "Berwickshire",
  "Breconshire",
  "Buckinghamshire",
  "Buteshire",
  "Caernarvonshire",
  "Caithness",
  "Cambridgeshire",
  "Cardiganshire",
  "Carmarthenshire",
  "Cheshire",
  "Clackmannanshire",
  "Cornwall",
  "Cumberland",
  "Denbighshire",
  "Derbyshire",
  "Devon",
  "Dorset",
  "Down",
  "Dumfriesshire",
  "Dunbartonshire",
  "Durham",
  "East Lothian",
  "East Riding of Yorkshire",
  "East Sussex",
  "Essex",
  "Fermanagh",
  "Fife",
  "Flintshire",
  "Glamorgan",
  "Gloucestershire",
  "Greater London",
  "Greater Manchester",
  "Hampshire",
  "Herefordshire",
  "Hertfordshire",
  "Huntingdonshire",
  "Inverness-shire",
  "Isle of Wight",
  "Kent",
  "Kincardineshire",
  "Kinross-shire",
  "Kirkcudbrightshire",
  "Lanarkshire",
  "Lancashire",
  "Leicestershire",
  "Lincolnshire",
  "Londonderry",
  "Merionethshire",
  "Merseyside",
  "Midlothian",
  "Monmouthshire",
  "Montgomeryshire",
  "Morayshire",
  "Nairnshire",
  "Norfolk",
  "Northamptonshire",
  "Northumberland",
  "Nottinghamshire",
  "Orkney",
  "Oxfordshire",
  "Peeblesshire",
  "Pembrokeshire",
  "Perthshire",
  "Radnorshire",
  "Renfrewshire",
  "Ross & Cromarty",
  "Roxburghshire",
  "Rutland",
  "Selkirkshire",
  "Shetland",
  "Shropshire",
  "Somerset",
  "Staffordshire",
  "Stirlingshire",
  "Suffolk",
  "Surrey",
  "Sutherland",
  "Tyne & Wear",
  "Tyrone",
  "Warwickshire",
  "West Lothian",
  "West Midlands",
  "West Riding of Yorkshire",
  "West Sussex",
  "Westmorland",
  "Wigtownshire",
  "Wiltshire",
  "Worcestershire",
  "Yorkshire"
]
        countries = [
            "England",
            "Scotland",
            "Wales",
            "Northern Ireland"
        ]
        if Countys.objects.exists():
            self.stdout.write(self.style.SUCCESS('Objects already exist. No action taken.'))
        else:
            for city in countys:
                if not Countys.objects.filter(name=city).exists():
                    Countys.objects.create(name=city, created_at=datetime.now(pytz.timezone('Europe/London')), agent=User.objects.get(email="admin@gmail.com"))
            self.stdout.write(self.style.SUCCESS('Objects created successfully.'))
            
        if Countries.objects.exists():
            self.stdout.write(self.style.SUCCESS('Objects already exist. No action taken.'))
        else:
            for country in countries:
                if not Countries.objects.filter(name=country).exists():
                    Countries.objects.create(name=country, created_at=datetime.now(pytz.timezone('Europe/London')), agent=User.objects.get(email="admin@gmail.com"))
            self.stdout.write(self.style.SUCCESS('Objects created successfully.'))


