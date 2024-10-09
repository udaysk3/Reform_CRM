from django.contrib import admin
from .models import (
    Action,
    Campaign,
    Stage,
    Document,
    Cities,
    HistoryId,
    Countys,
    Countries,
    Client_Council_Route,
)

from admin_app.models import Signature
from client_app.models import Clients, ClientArchive, CoverageAreas
from product_app.models import Product
from region_app.models import Councils
from funding_route_app.models import Route
from customer_journey_app.models import CJStage
from question_actions_requirements_app.models import Rule_Regulation, Questions
from customer_app.models import Customers, Answer

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
admin.site.register(CoverageAreas)
admin.site.register(Questions)
admin.site.register(Rule_Regulation)
admin.site.register(ClientArchive)
admin.site.register(Client_Council_Route)
admin.site.register(CJStage)
admin.site.register(Answer)
