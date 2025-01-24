from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.tfidf import save_groups_tfidf, save_people_tfidf
from parlacards.utils import get_playing_fields
from parladata.models import Organization


class Command(BaseCommand):
    help = "Set TFIDF"

    def handle(self, *args, **options):
        playing_fields = get_playing_fields(datetime.now())

        for playing_field in playing_fields:
            self.stdout.write("Start setting TFIDF for groups")
            save_groups_tfidf(playing_field, timestamp=datetime.now())

            self.stdout.write("Start setting TFIDF for people")
            save_people_tfidf(playing_field, timestamp=datetime.now())

            self.stdout.write("Done")
