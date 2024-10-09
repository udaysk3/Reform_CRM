from django.db import models
from region_app.models import Councils

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,)
    description = models.CharField(max_length=999, blank=True, null=True,)
    global_archive = models.BooleanField(default=False)
    documents = models.ManyToManyField("home.Document", related_name="product",)
    council = models.ManyToManyField(Councils, related_name="product",)
    stage = models.ManyToManyField("home.Stage", related_name="product")
    # rules_regulations = models.JSONField(blank= True, null=True)
    # is_parent = models.BooleanField(blank=True, null=True)
    # is_council = models.BooleanField(default=False)
    # is_client = models.BooleanField(default=False)
    # council_product = models.ManyToManyField('self', related_name="+")
    # client_product = models.ManyToManyField('self', related_name="+")

    def __str__(self):
        return f"{self.name}"
