from django.core.management.base import BaseCommand

from parlanotifications.management.commands.send_utils import send_emails
from parlanotifications.management.commands.send_speech_utils import (
    send_emails as send_speech_emails,
)


class Command(BaseCommand):
    help = "Send speech notifications"

    def handle(self, *args, **options):
        send_emails()
        send_speech_emails()
