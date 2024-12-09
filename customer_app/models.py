from django.db import models
from home.models import Action, Stage
from user.models import User

# Create your models here.


class Customers(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.TextField(max_length=999, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    constituency = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    campaign = models.ForeignKey('home.Campaign', related_name='customers', on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey('client_app.Clients', related_name='customers', on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, related_name= 'assigned_to', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    parent_customer = models.ForeignKey('self', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    primary_customer = models.BooleanField(default=False)
    energy_rating = models.CharField(max_length=2, blank=True, null=True)
    energy_certificate_link = models.URLField(max_length=999, blank=True, null=True)
    recommendations = models.TextField(max_length=999, blank=True, null=True)
    epc_data = models.JSONField(blank=True, null=True)
    route =  models.ForeignKey('funding_route_app.Route', related_name='customers', on_delete=models.SET_NULL, blank=True, null=True)
    stage_values = models.JSONField(blank= True, null=True)
    council = models.ForeignKey('region_app.Councils', on_delete=models.SET_NULL, null=True)
    closed = models.BooleanField(default=False)
    imported = models.BooleanField(default=False)


    def add_action(
        self,
        text=None,
        agent=None, closed=False, imported=False, created_at=None, talked_with=None, date_time=None, action_type=None, keyevents=False
    ):
        customer = self
        customer.closed = closed
        customer.save()
        return Action.objects.create(customer=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with, action_type=action_type, keyevents=keyevents)

    def get_created_at_action_history(self):
        return (Action.objects.filter(customer=self).order_by("-created_at"))

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Answer(models.Model):
    answer = models.JSONField(blank=True, null=True)
    route = models.ForeignKey(
        'funding_route_app.Route',
        related_name="answer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        'product_app.Product',
        related_name="answer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    stage = models.ForeignKey(
        Stage,
        related_name="answer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    question = models.ForeignKey(
        'question_actions_requirements_app.Questions',
        related_name="answer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    customer = models.ForeignKey(
        'customer_app.Customers',
        related_name="answer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    submit = models.BooleanField(default=False)
    file = models.FileField(upload_to='uploads/answers', blank=True, null=True)
    def __str__(self):
        return f"{self.route} {self.product} {self.stage} {self.question} {self.customer}"
