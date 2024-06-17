from django.core.management.base import BaseCommand
from home.models import Postcode
import os
import csv

class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        csv_filename = os.path.join(os.path.dirname(__file__), "../../ukpostcodes.csv")
        with open(csv_filename, "r", newline="") as csv_file:
            portfolio1 = csv.DictReader(csv_file)
            list_of_dict = list(portfolio1)

        objs = [
            Postcode(
                postcode=row["postcode"],
                latitude=row["latitude"],
                longitude=row["longitude"],
            )
            for row in list_of_dict
            if row["postcode"] and row["latitude"] and row["longitude"]
        ]

        if objs:
            Postcode.objects.bulk_create(objs)
            self.stdout.write(
                self.style.SUCCESS(f"{len(objs)} postcodes created successfully.")
            )
        else:
            self.stdout.write(self.style.WARNING("No valid postcodes to create."))
