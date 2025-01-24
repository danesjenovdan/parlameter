from django.core.management.base import BaseCommand, CommandError

from parladata.update_utils import notify_editors_for_new_data


class Command(BaseCommand):
    help = "Send daily notifications"

    def handle(self, *args, **options):
        self.stdout.write("Checking for new data")

        notify_editors_for_new_data()
