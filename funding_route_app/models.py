from django.db import models

# Create your models here.


class Route(models.Model):
    name = models.CharField(max_length=999, blank= True, null=True)
    managed_by = models.CharField(max_length=999, blank= True, null=True)
    main_contact = models.CharField(max_length=999, blank= True, null=True)
    telephone = models.CharField(max_length=15, blank= True, null=True)
    email = models.EmailField(max_length=255)
    council = models.ManyToManyField('region_app.Councils',related_name='routes')
    description = models.CharField(max_length=999, blank= True, null=True)
    documents = models.ManyToManyField('home.Document',related_name='route')
    order = models.IntegerField(blank=True, null=True)
    global_archive = models.BooleanField(default=False)
    product = models.ManyToManyField("product_app.Product", related_name="route")
    # rules_regulations = models.JSONField(blank=True, null=True)
    # sub_rules_regulations = models.JSONField(blank=True, null=True)
    # council_route = models.ManyToManyField("self", related_name="+")
    # client_route = models.ManyToManyField("self", related_name="+")
    # is_parent = models.BooleanField(blank=True, null=True)
    # is_council = models.BooleanField(blank=True, null=True)
    # is_client = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

