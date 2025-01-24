from django.core.management.base import BaseCommand

from parladata.models.common import EducationLevel


class Command(BaseCommand):
    help = "Create education levels"

    def handle(self, *args, **options):
        self.stdout.write("Creating education levels")

        level_text = ["1", "2", "3", "4", "5", "6/1", "6/2", "7", "8/1", "8/2"]

        for i, level in enumerate(level_text):
            EducationLevel(text=level, order=i).save()
