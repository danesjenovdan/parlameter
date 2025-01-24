from django.core.management.base import BaseCommand, CommandError

from parladata.update_utils import set_vote_session


class Command(BaseCommand):
    help = "Set session to votes "

    def handle(self, *args, **options):
        self.stdout.write("Start setting session to votes")

        set_vote_session(self.stdout.write)
