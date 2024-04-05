from django.db import models
from user.models import User

class Customers(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.TextField(max_length=999, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    constituency = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    campaign = models.ForeignKey('Campaign', related_name='customers', on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey('Client', related_name='customers', on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    parent_customer = models.ForeignKey('self', blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    primary_customer = models.BooleanField(default=False)
    energy_rating = models.CharField(max_length=2, blank=True, null=True)
    energy_certificate_link = models.URLField(max_length=999, blank=True, null=True)
    recommendations = models.TextField(max_length=999, blank=True, null=True)
    
    def add_action(
        self,
        text,
        agent, date_time=None, imported=False, created_at=None, talked_with=None, funding_route=None,
    ):
        return Action.objects.create(customer=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with)

    def get_created_at_action_history(self):
        return (Action.objects.filter(customer=self).order_by("-created_at"))
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Client(models.Model):
    name = models.CharField(max_length=255,blank=True, null=True)
    main_contact = models.CharField(max_length=225,blank=True, null=True)
    telephone = models.CharField(max_length=225,blank=True, null=True)
    email= models.EmailField(max_length=225,blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, related_name='campaigns', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.client.name} {self.name}"
    
class Route(models.Model):
    name = models.CharField(max_length=999, blank= True, null=True)
    managed_by = models.CharField(max_length=999, blank= True, null=True)
    main_contact = models.CharField(max_length=999, blank= True, null=True)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    council = models.ForeignKey('home.Councils', on_delete=models.CASCADE, null=True, blank= True)
    
class Councils(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def get_created_at_council_action_history(self):
        return (Action.objects.filter(council=self).order_by("-created_at"))
    
    def add_council_action(
        self,
        text,
        agent, date_time=None, imported=False, created_at=None, talked_with=None, council=None,
    ):
        return Action.objects.create(council=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with)

    def __str__(self):
        return f"{self.id}"
    
class Action(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True)
    council = models.ForeignKey(Councils, on_delete=models.CASCADE, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(max_length=999, blank= True, null=True)
    imported = models.BooleanField(default=False)
    talked_with = models.CharField(max_length=225, blank= True, null=True)

class Stage(models.Model):
    name = models.CharField(max_length=999, blank= True, null=True)
    council = models.ForeignKey(Councils, related_name='stage', on_delete=models.CASCADE, null=True)
    route = models.ForeignKey(Route, related_name='stage', on_delete=models.CASCADE, null=True)
    fields = models.JSONField()