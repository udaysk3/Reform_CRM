from django.db import models
from datetime import datetime

import pytz

utc = pytz.UTC

class Customers(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    home_owner = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now())

    def add_action(self, date_time, text, date , time):
        return Action.objects.create(customer=self, date_time=date_time, text=text, date=date, time=time)

    def get_action_future(self):
        return (
            Action.objects.filter(customer=self)
            .filter(date_time__gte=datetime.now().replace(tzinfo=utc))
            .order_by("-date_time")
        )

    def get_action_history(self):
        return (
            Action.objects.filter(customer=self)
            .filter(date_time__lt=datetime.now().replace(tzinfo=utc))
            .order_by("-date_time")
        )

class Action(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    date= models.DateField(null=True, blank=True)
    time= models.TimeField(null=True, blank=True)
    text = models.TextField(max_length=999)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name} - {self.date_time}"
