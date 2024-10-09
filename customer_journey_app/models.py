from django.db import models
from home.models import Stage

# Create your models here.


class CJStage(models.Model):
    route = models.ForeignKey(
        'funding_route_app.Route',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    product = models.ForeignKey(
        'product_app.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    order = models.IntegerField(blank=True, null=True)