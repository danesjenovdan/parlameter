from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.update import (
    run_speech_analyses,
    run_speech_analyses_for_playing_field_sessions,
)
from parladata.models.organization import Organization


class Command(BaseCommand):
    help = "Seeds sparse scores"

    def add_arguments(self, parser):
        parser.add_argument("--start_time", type=str, default="")
        parser.add_argument("--end_of_playing_field_sessions", type=str, default="")

    def handle(self, *args, **options):

        input_timestamp = options["start_time"]
        playing_field_id = options["end_of_playing_field_sessions"]
        if input_timestamp:
            timestamp = datetime.fromisoformat(input_timestamp)

            run_speech_analyses(timestamp, self.stdout.write)
        elif playing_field_id:
            run_speech_analyses_for_playing_field_sessions(
                playing_field_id, self.stdout.write
            )
