from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    dashboard = models.BooleanField(default=False)
    customer = models.BooleanField(default=False)
    client = models.BooleanField(default=False)
    council = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    product = models.BooleanField(default=False)
    globals = models.BooleanField(default=False)
    finance = models.BooleanField(default=False)
    hr = models.BooleanField(default=False)
    security = models.BooleanField(default=False)