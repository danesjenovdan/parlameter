from django.core.management.base import BaseCommand, CommandError

from parladata.data_tests import run_tests


class Command(BaseCommand):
    help = "Data validation"

    def handle(self, *args, **options):
        self.stdout.write("Start data valdiation")
        run_tests()
