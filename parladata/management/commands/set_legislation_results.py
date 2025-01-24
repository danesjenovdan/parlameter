from django.core.management.base import BaseCommand, CommandError

from parladata.update_helpers.methods import set_legislation_results


class Command(BaseCommand):
    help = "Set result to legislation without result"

    def handle(self, *args, **options):
        self.stdout.write("Start setting legislation results")
        set_legislation_results()
