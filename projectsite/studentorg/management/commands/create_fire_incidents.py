import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from studentorg.models import FireLocation, FireIncident


class Command(BaseCommand):
    help = "Generate 10 fire locations and 50 random fire incidents"

    def handle(self, *args, **kwargs):
        # Create 10 fire locations (barangays in PPC)
        barangays = [
            "San Pedro",
            "San Miguel",
            "San Jose",
            "San Manuel",
            "San Isidro",
            "Santa Monica",
            "Tagburos",
            "Tiniguiban",
            "Manggahan",
            "Mandaragat",
        ]

        for barangay in barangays:
            FireLocation.objects.create(
                country=f"Barangay {barangay}, PPC, Philippines"
            )

        self.stdout.write(self.style.SUCCESS("Successfully created 10 fire locations."))

        # Create 50 random incidents
        severity_levels = ["Low", "Medium", "High"]
        now = datetime.now()

        locations = FireLocation.objects.all()

        for _ in range(50):
            # Random date within the last year
            days_ago = random.randint(0, 365)
            random_date = now - timedelta(days=days_ago)

            # Random severity level
            severity = random.choice(severity_levels)

            # Random location
            location = random.choice(locations)

            # Create FireIncident
            FireIncident.objects.create(
                date_time=random_date, severity_level=severity, location=location
            )

        self.stdout.write(self.style.SUCCESS("Successfully created 50 fire incidents."))
