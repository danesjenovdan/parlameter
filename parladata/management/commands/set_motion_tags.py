from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Set motion tags"

    def handle(self, *args, **options):
        self.stdout.write("Start setting motion tags")

        self.stdout.write("PASS")
