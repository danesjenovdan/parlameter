from django.core.management.base import BaseCommand, CommandError

from parladata.models import Organization


class Command(BaseCommand):
    help = "Merges people together"

    def add_arguments(self, parser):
        parser.add_argument("people", nargs="+")

    def handle(self, *args, **options):
        self.stdout.write("I am about to start new data nedded for parlameter")
        self.stdout.write("\n")

        dz = Organization(name="DZ")
        dz.save()
        coalition = Organization(
            name="Coalition", classification="Coalition", parent=dz
        )
        coalition.save()
        opposition = Organization(
            name="Opposition", classification="Opposition", parent=dz
        )
        opposition.save()

        self.stdout.write("\n")
        self.stdout.write("DONE")
