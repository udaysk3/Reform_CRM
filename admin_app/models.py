from django.db import models
from user.models import User

# Create your models here.


class Signature(models.Model):
    signature = models.TextField(max_length=999, blank=True, null=True)
    signature_img = models.FileField(upload_to="signatures", blank= True, null=True)
    employee = models.ManyToManyField(User, blank=True, null=True, related_name="signature")
    
class Email(models.Model):
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    body = models.TextField(max_length=9999)
    
    def __str__(self):
        return f"{self.name}"

class Reason(models.Model):
    name = models.CharField(max_length=255)
    reason = models.TextField(max_length=999)
    
    def __str__(self):
        return f"{self.name}"
