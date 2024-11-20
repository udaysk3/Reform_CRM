from django.db import models
from user.models import User

class Document(models.Model):
    document = models.FileField(upload_to="documents", blank= True, null=True)
    is_product = models.BooleanField(default=False,blank=True,null=True)
    is_route = models.BooleanField(default=False,blank=True,null=True)
    is_council = models.BooleanField(default=False,blank=True,null=True)
    is_client = models.BooleanField(default=False,blank=True,null=True)

class Campaign(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,)
    description = models.CharField(max_length=999, blank=True, null=True,)
    client = models.ForeignKey('client_app.Clients', related_name='campaigns', on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name} {self.name}"


class Cities(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return f"{self.name}"

class Countys(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return f"{self.name}"

class Countries(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return f"{self.name}"

class Action(models.Model):
    customer = models.ForeignKey('customer_app.Customers', on_delete=models.CASCADE, null=True)
    client = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE, null=True)
    council = models.ForeignKey('region_app.Councils', on_delete=models.CASCADE, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    text = models.TextField(max_length=999, blank= True, null=True)
    imported = models.BooleanField(default=False)
    talked_with = models.CharField(max_length=225, blank= True, null=True)
    action_type = models.CharField(max_length=225, blank= True, null=True)
    keyevents = models.BooleanField(default=False)

class Stage(models.Model):
    name = models.CharField(max_length=999, blank= True, null=True)
    council = models.ForeignKey('region_app.Councils', related_name='stage', on_delete=models.CASCADE, null=True)
    order = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=999, blank=True, null=True)
    fields = models.JSONField(blank= True, null=True)
    client = models.ForeignKey('client_app.Clients', related_name='stage', on_delete=models.CASCADE, null=True)
    global_archive = models.BooleanField(default=False)
    documents = models.ManyToManyField(
        "home.Document", related_name="stage",
    )
    templateable = models.BooleanField(default=False)
    question = models.ManyToManyField("question_actions_requirements_app.Questions", related_name="stage")

    def __str__(self):
        return f"{self.name}"




class HistoryId(models.Model):
    history_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.history_id}"


class Client_Council_Route(models.Model):
    client = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE, null=True, blank=True, related_name='client_council_route')
    council = models.ForeignKey('region_app.Councils', on_delete=models.CASCADE, null=True, blank=True, related_name='client_council_route')
    route = models.ForeignKey('funding_route_app.Route', on_delete=models.CASCADE, null=True, blank=True, related_name='client_council_route')

class Suggestion(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=999, blank=True, null=True)
    file = models.FileField(upload_to="suggestion", blank=True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='file_suggestion')