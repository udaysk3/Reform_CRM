from django.db import models
from datetime import datetime
from user.models import User
import pytz


class Customers(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.now())
    campaign = models.ForeignKey('Campaign', related_name='customers', on_delete=models.CASCADE, null=True)
    client = models.ForeignKey('Client', related_name='customers', on_delete=models.CASCADE, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    def add_action(
        self,
        text,
        agent, date_time=None, imported=False
    ):
        return Action.objects.create(customer=self, date_time=date_time, text=text, agent=agent, imported=imported)

    def get_created_at_action_history(self):
        return (Action.objects.filter(customer=self).order_by("-added_date_time"))

    def get_action_history(self):
        return (Action.objects.filter(customer=self).order_by("-date_time"))

class Action(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    date_time = models.DateTimeField(blank=True, null=True)
    london_tz = pytz.timezone('Europe/London')
    added_date_time = models.DateTimeField(default=datetime.now(london_tz))
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(max_length=999)
    imported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name} - {self.date_time}"

class Client(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Campaign(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, related_name='campaigns', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name} {self.name}"
    
    