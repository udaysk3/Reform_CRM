from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None,  **extra_fields):
        extra_fields = {"is_staff": False, "is_superuser": False, **extra_fields}
        if not email:
            raise ValueError("Users must have an email address")
        if first_name and last_name:
            user = User(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        else:
            user = User(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields = {
            "dashboard": True,
            "customer": True,
            "client": True,
            "archive": True,
            "funding_route":True,
            "admin": True,
            "stage": True,
            "product": True,
            "finance": True,
            "council":True,
            "hr": True,
            "is_staff": True,
            "is_superuser": True,
            **extra_fields,
        }

        user = self.create_user(email=email, password=password,  **extra_fields)

        return user

USER_CHOICES = [
    ('employee', 'Employee'),
    ('HR', 'HR'),
    ('Admin', 'Admin'),
]
class User(AbstractUser):
    username = None
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    dashboard = models.BooleanField(default=True)
    customer = models.BooleanField(default=True)
    client = models.BooleanField(default=True)
    archive = models.BooleanField(default=True)
    council = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    stage = models.BooleanField(default=False)
    product = models.BooleanField(default=False)
    finance = models.BooleanField(default=False)
    funding_route = models.BooleanField(default=False)
    hr = models.BooleanField(default=False)
    
    objects = UserManager()