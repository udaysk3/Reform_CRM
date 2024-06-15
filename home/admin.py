from django.contrib import admin
from .models import (
    Action,
    Customers,
    Clients,
    Campaign,
    Councils,
    Route,
    Stage,
    Document,
    Cities,
    HistoryId,
    Countys,
    Countries,
    Signature,
    Product,
    Postcode,
)

admin.site.register(Action)
admin.site.register(Customers)
admin.site.register(Clients)
admin.site.register(Campaign)
admin.site.register(Councils)
admin.site.register(Route)
admin.site.register(Stage)
admin.site.register(Document)
admin.site.register(Cities)
admin.site.register(HistoryId)
admin.site.register(Countys)
admin.site.register(Countries)
admin.site.register(Signature)
admin.site.register(Product)
admin.site.register(Postcode)
