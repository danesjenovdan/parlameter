from django.core.management.base import BaseCommand, CommandError

from parladata.update_utils import set_results_to_votes


class Command(BaseCommand):
    help = "Set result to votes without result"

    def add_arguments(self, parser):
        parser.add_argument(
            "--majority",
            nargs=1,
            help="Type if majority [relative_normal, absolute_normal]",
        )

    def handle(self, *args, **options):
        self.stdout.write("Start setting results")

        majority = options["majority"][0]

        set_results_to_votes(majority)
