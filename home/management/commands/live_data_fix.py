from django.core.management.base import BaseCommand
from home.models import Document, Suggestion, Sub_suggestions
from django.db.models import Q
from customer_journey_app.models import CJStage
import os

class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        try:
            # print(CJStage.objects.filter(questions__isnull=False).count())
            # Sub_suggestions.objects.filter(Q(status = None) | Q(status="New")).update(status = 'In Review')
            self.stdout.write(self.style.SUCCESS("Completed processing"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
