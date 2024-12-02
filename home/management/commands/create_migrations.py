from django.core.management.base import BaseCommand
from home.models import Document, Suggestion
import os

class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        try:
            suggestions = Suggestion.objects.all()
            for suggestion in suggestions:
                if suggestion.file:
                    document = Document.objects.create(
                        document=suggestion.file,
                    )
                    suggestion.files.add(document)
                    suggestion.save()      
                print(suggestion.files.all())
                
            self.stdout.write(self.style.SUCCESS("Completed processing"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
