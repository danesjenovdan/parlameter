from django.core.management.base import BaseCommand, CommandError

from parladata.models import Person


class Command(BaseCommand):
    help = "Merges people together"

    def add_arguments(self, parser):
        parser.add_argument(
            "--original",
            nargs=1,
            help="Original person",
        )

        parser.add_argument(
            "--fake",
            nargs="+",
            help="Fake people",
        )

    def handle(self, *args, **options):
        real_person_id = options["original"][0]
        fake_person_ids = options["fake"]
        self.merge_people(real_person_id, fake_person_ids, self.stdout.write)

    def merge_people(self, real_person_id, fake_person_ids, print_method):

        print_method("Real person id: %s" % real_person_id)
        print_method("Fake people ids: %s" % ", ".join(fake_person_ids))
        print_method("\n")

        # check if real person exists
        try:
            real_person = Person.objects.get(id=int(real_person_id))
        except Person.DoesNotExist:
            raise CommandError("No real person found")

        # check if fake people exist
        if (
            Person.objects.filter(
                id__in=[int(person_id) for person_id in fake_person_ids]
            ).count()
            > 0
        ):
            fake_people = Person.objects.filter(
                id__in=[int(person_id) for person_id in fake_person_ids]
            )
        else:
            raise CommandError("No fake people found")

        # deal with ballots
        print_method("Real person has %d ballots." % real_person.ballots.all().count())
        for fake_person in fake_people:
            print_method(
                "Fake person %d has %d ballots."
                % (fake_person.id, fake_person.ballots.all().count())
            )
            print_method("Moving ballots to real person...")
            for ballot in fake_person.ballots.all():
                ballot.personvoter = real_person
                ballot.save()
            print_method("Done with moving.")

        print_method("\n")

        print_method(
            "Real person has %d speeches." % real_person.speeches.all().count()
        )
        for fake_person in fake_people:
            print_method(
                "Fake person %d has %d speeches."
                % (fake_person.id, fake_person.speeches.all().count())
            )
            print_method("Moving speeches to real person...")
            for speech in fake_person.speeches.all():
                speech.speaker = real_person
                speech.save()
            print_method("Done with moving.")

        print_method(
            f"Real person is author of {real_person.authored_questions.all().count()} questions."
        )
        for fake_person in fake_people:
            print_method(
                f"Fake person {fake_person.id} is author of {fake_person.authored_questions.all().count()} questions."
            )
            print_method("Moving questions to real person...")
            for question in fake_person.authored_questions.all():
                question.person_authors.remove(fake_person)
                question.person_authors.add(real_person)
                question.save()
            print_method("Done with moving.")

        print_method(
            f"Real person is recipient of {real_person.received_questions.all().count()} questions."
        )
        for fake_person in fake_people:
            print_method(
                f"Fake person {fake_person.id} is recipient of {fake_person.received_questions.all().count()} questions."
            )
            print_method("Moving questions to real person...")
            for question in fake_person.received_questions.all():
                question.recipient_people.remove(fake_person)
                question.recipient_people.add(real_person)
                question.save()
            print_method("Done with moving.")

        for fake_person in fake_people:
            fake_parser_names = fake_person.parser_names.split("|")
            for fake_parser_name in fake_parser_names:
                real_person.add_parser_name(fake_parser_name)
            print_method(str(fake_person.delete()))
        real_person.save()

        print_method("\n")
        print_method("DONE")
