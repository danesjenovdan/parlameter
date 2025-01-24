from django.core.management.base import BaseCommand, CommandError

from parladata.models import Session


class Command(BaseCommand):
    help = "Merges people together"

    def handle(self, *args, **options):
        self.stdout.write("I am about to delete all sessions")
        self.stdout.write("\n")
        Session.objects.all().delete()
        self.stdout.write("\n")
        self.stdout.write("DONE")
