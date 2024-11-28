from django.db import models
from home.models import Stage
from security_app.models import Role

class CJStage(models.Model):
    route = models.ForeignKey(
        'funding_route_app.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    product = models.ForeignKey(
        'product_app.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    client = models.ForeignKey(
        'client_app.Clients',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="CJStage",
    )
    question = models.ForeignKey("question_actions_requirements_app.Questions", on_delete=models.SET_NULL, null=True, blank=True)
    questions = models.JSONField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)