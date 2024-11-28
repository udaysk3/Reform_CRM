from django.db import models
from user.models import User

# Create your models here.


class Councils(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    postcodes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class RegionArchive(models.Model):
    route = models.ForeignKey('funding_route_app.Route', on_delete=models.CASCADE, null=True, blank=True, related_name='region_archive')
    council = models.ForeignKey(Councils, on_delete=models.CASCADE, null=True, blank=True, related_name='region_archive')