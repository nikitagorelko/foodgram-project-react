import csv
import io
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Management-команда для импорта данных ингредиентов
    из файла CSV в БД Django-проекта."""

    def handle(self, *args, **options):
        del args, options
        with io.open(
            os.path.join(settings.BASE_DIR.parent / 'data/ingredients.csv'),
            "r",
            encoding="utf-8",
        ) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                Ingredient.objects.create(name=row[0], measurement_unit=row[1])
