from django.db import models
from user.models import User

class Customers(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.TextField(max_length=999, blank=True, null=True)
    address = models.TextField(max_length=999, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    constituency = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    campaign = models.ForeignKey('Campaign', related_name='customers', on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey('Clients', related_name='customers', on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    assigned_to = models.ForeignKey(User, related_name= 'assigned_to', on_delete=models.DO_NOTHING, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    parent_customer = models.ForeignKey('self', blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    primary_customer = models.BooleanField(default=False)
    energy_rating = models.CharField(max_length=2, blank=True, null=True)
    energy_certificate_link = models.URLField(max_length=999, blank=True, null=True)
    recommendations = models.TextField(max_length=999, blank=True, null=True)
    route =  models.ForeignKey('Route', related_name='customers', on_delete=models.SET_NULL, blank=True, null=True)
    stage_values = models.JSONField(blank= True, null=True)
    council = models.ForeignKey('Councils', on_delete=models.SET_NULL, null=True)
    closed = models.BooleanField(default=False)
    imported = models.BooleanField(default=False)


    def add_action(
        self,
        text=None,
        agent=None, closed=False, imported=False, created_at=None, talked_with=None, date_time=None, action_type=None, keyevents=False
    ):
        customer = self
        customer.closed = closed
        customer.save()
        return Action.objects.create(customer=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with, action_type=action_type, keyevents=keyevents)

    def get_created_at_action_history(self):
        return (Action.objects.filter(customer=self).order_by("-created_at"))

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Clients(models.Model):
    acc_number = models.CharField(max_length=255, blank=True, null=True)
    sort_code = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=255, blank=True, null=True)
    bic_swift = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_phno = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    house_name = models.CharField(max_length=255, blank=True, null=True)
    street_name = models.TextField(max_length=999, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    parent_client = models.ForeignKey('self', blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    primary_client = models.BooleanField(default=False)
    council = models.ForeignKey('Councils', on_delete=models.SET_NULL, null=True)
    closed = models.BooleanField(default=False)
    imported = models.BooleanField(default=False)
    route = models.ManyToManyField(
        "home.Route", related_name="client",
    )
    

    def add_action(
        self,
        text=None,
        agent=None, closed=False, imported=False, created_at=None, talked_with=None, date_time=None, action_type=None, keyevents=False
    ):
        client = self
        client.closed = closed
        client.save()
        return Action.objects.create(client=self, date_time=date_time, text=text, agent=agent, imported=imported, created_at=created_at, talked_with=talked_with, action_type=action_type, keyevents=keyevents)

    def get_created_at_action_history(self):
        return (Action.objects.filter(client=self).order_by("-created_at"))

    def __str__(self):
        return f"{self.company_name}"

class Route(models.Model):
    name = models.CharField(max_length=999, blank= True, null=True)
    managed_by = models.CharField(max_length=999, blank= True, null=True)
    main_contact = models.CharField(max_length=999, blank= True, null=True)
    telephone = models.CharField(max_length=15, blank= True, null=True)
    email = models.EmailField(max_length=255)
    council = models.ManyToManyField('home.Councils',related_name='routes')
    description = models.CharField(max_length=999, blank= True, null=True)
    documents = models.ManyToManyField('home.Document',related_name='route')
    archive = models.BooleanField(default=False)
    rules_regulations = models.JSONField(blank=True, null=True)
    sub_rules_regulations = models.JSONField(blank=True, null=True)
    council_route = models.ManyToManyField("self", related_name="+")
    client_route = models.ManyToManyField("self", related_name="+")
    parent_route = models.BooleanField(blank=True, null=True)
    main_route = models.BooleanField(blank=True, null=True)
    product = models.ManyToManyField("home.Product", related_name="route")


class Document(models.Model):
    document = models.FileField(upload_to="documents", blank= True, null=True)


class Councils(models.Model):
    name = models.CharField(max_length=999, unique=True)
    created_at = models.DateTimeField(blank= True, null=True)
    agent = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return f"{self.name}"

class Campaign(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,)
    description = models.CharField(max_length=999, blank=True, null=True,)
    client = models.ForeignKey(Clients, related_name='campaigns', on_delete=models.CASCADE)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name} {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True,)
    description = models.CharField(max_length=999, blank=True, null=True,)
    archive = models.BooleanField(default=False)
    rules_regulations = models.JSONField(blank= True, null=True)
    documents = models.ManyToManyField(
        "home.Document", related_name="product", 
    )
    client = models.ManyToManyField(
        Clients,
        related_name="product",
    )
    stage = models.ManyToManyField("home.Stage", related_name="product")

    def __str__(self):
        return f"{self.name}"


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
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True)
    council = models.ForeignKey(Councils, on_delete=models.CASCADE, null=True)
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
    council = models.ForeignKey(Councils, related_name='stage', on_delete=models.CASCADE, null=True)
    order = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=999, blank=True, null=True)
    fields = models.JSONField(blank= True, null=True)
    client = models.ForeignKey(Clients, related_name='stage', on_delete=models.CASCADE, null=True)
    documents = models.ManyToManyField(
        "home.Document", related_name="stage",
    )
    templateable = models.BooleanField(default=False)
    question = models.ManyToManyField("home.Questions", related_name="stage")


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


class HistoryId(models.Model):
    history_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.history_id}"

class Signature(models.Model):
    signature = models.TextField(max_length=999, blank=True, null=True)
    signature_img = models.FileField(upload_to="signatures", blank= True, null=True)

class Postcode(models.Model):
    postcode = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.postcode}"

class CoverageAreas(models.Model):
    client = models.ForeignKey(Clients, related_name='coverage_areas', on_delete=models.CASCADE)
    postcode = models.CharField(max_length=255, blank=True, null=True)

class Questions(models.Model):
    question = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    answer_frequency = models.IntegerField(blank=True, null=True)
    rules_regulations = models.JSONField(blank=True, null=True)

class QAction(models.Model):
    action = models.CharField(max_length=255, blank=True, null=True)
    script = models.TextField(max_length=255, blank=True, null=True)
