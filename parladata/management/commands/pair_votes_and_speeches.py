from django.core.management.base import BaseCommand, CommandError

from parladata.update_utils import pair_motions_with_speeches


class Command(BaseCommand):
    help = "Connecting votes with speeches "

    def handle(self, *args, **options):
        self.stdout.write("Start connecting votes with speeches")

        pair_motions_with_speeches()
