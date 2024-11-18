from django.db import models
from home.models import Stage

class Questions(models.Model):
    question = models.CharField(max_length=9999, blank=True, null=True)
    type = models.CharField(max_length=9999, blank=True, null=True)
    answer_frequency = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    parameter = models.CharField(max_length=9999, blank=True, null=True)
    is_archive = models.BooleanField(default=False)
    is_client_archive = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.question}"

class Rule_Regulation(models.Model):
    rules_regulation = models.JSONField(blank=True, null=True)
    is_client = models.BooleanField(default=False)
    route = models.ForeignKey(
        'funding_route_app.Route',
        related_name="rules_regulation",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        'product_app.Product',
        related_name="rules_regulation",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    stage = models.ForeignKey(
        Stage,
        related_name="rules_regulation",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    question = models.ForeignKey(
        Questions,
        related_name="rules_regulation",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    def __str__(self):
        return f"{self.route} {self.product} {self.stage} {self.question}"

