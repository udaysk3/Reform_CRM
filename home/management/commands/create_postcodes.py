from django.core.management.base import BaseCommand
from home.models import Councils
from user.models import User
import os
import csv
from django.db import transaction
import datetime
from concurrent.futures import ThreadPoolExecutor


class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        try:
            csv_filename = os.path.join(
                os.path.dirname(__file__), "../../postcodes.csv"
            )
            if not os.path.isfile(csv_filename):
                self.stdout.write(
                    self.style.ERROR(f"CSV file does not exist: {csv_filename}")
                )
                return

            with open(csv_filename, "r", newline="", encoding="utf-8-sig") as csv_file:
                portfolio1 = csv.DictReader(csv_file)
                list_of_dict = list(portfolio1)
            self.stdout.write(
                self.style.SUCCESS(f"Loaded {len(list_of_dict)} rows from CSV")
            )

            admin_user = User.objects.get(email="admin@gmail.com")

            batch_size = 10000
            total_rows = len(list_of_dict)
            num_batches = (total_rows // batch_size) + 1

            def process_batch(start_index):
                end_index = min(start_index + batch_size, total_rows)
                rows = list_of_dict[start_index:end_index]
                councils_to_update = []
                councils_to_create = []

                for row in rows:
                    try:
                        postcode = row["Postcode"].strip()
                        district = row["District"].strip()
                        print(postcode,district)
                        if postcode and district:
                            council_instance = Councils.objects.filter(
                                name=district
                            ).first()
                            if council_instance:
                                if council_instance.postcodes:
                                    council_instance.postcodes += "," + postcode
                                else:
                                    council_instance.postcodes = postcode
                                councils_to_update.append(council_instance)
                            else:
                                council_instance = Councils(
                                    name=district,
                                    postcodes=postcode,
                                    created_at=datetime.datetime.now(),
                                    agent=admin_user,
                                )
                                councils_to_create.append(council_instance)
                    except KeyError as e:
                        self.stdout.write(self.style.ERROR(f"Missing key in row: {e}"))
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error processing row: {e}")
                        )

                if councils_to_create:
                    Councils.objects.bulk_create(
                        councils_to_create, batch_size=batch_size
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created {len(councils_to_create)} councils"
                        )
                    )

                if councils_to_update:
                    Councils.objects.bulk_update(
                        councils_to_update, ["postcodes"], batch_size=batch_size
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated {len(councils_to_update)} councils"
                        )
                    )

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [
                    executor.submit(process_batch, i)
                    for i in range(0, total_rows, batch_size)
                ]
                for future in futures:
                    future.result()

            self.stdout.write(self.style.SUCCESS("Completed processing"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
