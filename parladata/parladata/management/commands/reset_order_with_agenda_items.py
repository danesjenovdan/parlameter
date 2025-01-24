from django.core.management.base import BaseCommand

from parladata.update_utils import reset_order_on_speech


class Command(BaseCommand):
    help = "Set motion tags"

    def handle(self, *args, **options):
        reset_order_on_speech()
