from django.core.management.base import BaseCommand, CommandError

from parladata.models import Person


class Command(BaseCommand):
    help = "Merges people together"

    def add_arguments(self, parser):
        parser.add_argument("people", nargs="+")

    def handle(self, *args, **options):
        self.stdout.write(
            "I am about to delete the followig people: %s"
            % ", ".join(options["people"])
        )
        self.stdout.write("\n")

        # check if people exist
        people = Person.objects.filter(
            id__in=[int(person_id) for person_id in options["people"]]
        )
        if people.count() == 0:
            self.stderr.write("No matching people found")
            self.stdout.write("\n")

        # delete people
        people.delete()

        self.stdout.write("\n")
        self.stdout.write("DONE")
