from django.core.management.base import BaseCommand

from parlanotifications.management.commands.send_utils import send_emails


class Command(BaseCommand):
    help = "Send speech notifications"

    def handle(self, *args, **options):
        send_emails()
