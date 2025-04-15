import json
from django.core.management.base import BaseCommand
from beneficiary.models import Province, City

class Command(BaseCommand):
    help = "Populate Province and City tables with data from province_city.json"

    def handle(self, *args, **kwargs):
        # Path to the JSON file
        json_path = 'user/data/province_city.json'

        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Populate Province and City tables
        for entry in data:
            province_name = entry["province-fa"]
            cities = entry["cities"]
            # Create Province
            province, created = Province.objects.get_or_create(province_name=province_name)

            # Create Cities
            for city_name in cities:
                city_name = city_name['city-fa']
                City.objects.get_or_create(city_name=city_name, province=province)

        self.stdout.write(self.style.SUCCESS("Provinces and Cities populated successfully!"))
