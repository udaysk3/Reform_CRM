from django.contrib import admin
from .models import Action, Customers, Client, Campaign, FundingRoutes

admin.site.register(Action)
admin.site.register(Customers)
admin.site.register(Client)
admin.site.register(Campaign)
admin.site.register(FundingRoutes)