from django.db import models
from home.models import Action, Stage
from user.models import User

class Clients(models.Model):
    acc_number = models.CharField(max_length=255, blank=True, null=True)
    sort_code = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=255, blank=True, null=True)
    bic_swift = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_phno = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.TextField(max_length=999, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    energy_rating = models.CharField(max_length=2, blank=True, null=True)
    energy_certificate_link = models.URLField(max_length=999, blank=True, null=True)
    constituency = models.CharField(max_length=255, blank=True, null=True)
    recommendations = models.TextField(max_length=999, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    parent_client = models.ForeignKey('self', blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    primary_client = models.BooleanField(default=False)
    council = models.ForeignKey('region_app.Councils', on_delete=models.SET_NULL, null=True)
    closed = models.BooleanField(default=False)
    imported = models.BooleanField(default=False)
    route = models.ManyToManyField(
        "funding_route_app.Route", related_name="client",
    )
    product = models.ManyToManyField(
        "product_app.Product", related_name="client",
    )

    def add_action(
        self,
        text=None,
        agent=None, closed=False, imported=False, created_at=None, talked_with=None, date_time=None, action_type=None, keyevents=False
    ):
        client = self
        client.closed = closed
        client.save()
        return Action.objects.create(client=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with, action_type=action_type, keyevents=keyevents)

    def get_created_at_action_history(self):
        return (Action.objects.filter(client=self).order_by("-created_at"))

    def __str__(self):
        return f"{self.company_name}"

class CoverageAreas(models.Model):
    client = models.ForeignKey('client_app.Clients', related_name='coverage_areas', on_delete=models.CASCADE)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    council = models.ForeignKey('region_app.Councils', on_delete=models.CASCADE, null=True)

class ClientArchive(models.Model):
    client = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE, null=True, blank=True, related_name='client_archive')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True, related_name='client_archive')
    route = models.ForeignKey('funding_route_app.Route', on_delete=models.CASCADE, null=True, blank=True, related_name='client_archive')
    councils = models.ForeignKey('region_app.Councils', on_delete=models.CASCADE, null=True, blank=True, related_name='client_archive')
    product = models.ForeignKey('product_app.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='client_archive')