from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.tfidf import save_sessions_tfidf_for_fresh_sessions
from parlacards.utils import get_playing_fields
from parladata.models.common import Mandate
from parladata.models.organization import Organization
from parladata.models.speech import Speech


class Command(BaseCommand):
    help = "Set TFIDF for sessions"

    def handle(self, *args, **options):
        self.stdout.write("Start setting TFIDF")
        mandate = Mandate.get_active_mandate_at(datetime.now())
        if mandate:
            from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
                datetime.now()
            )
            playing_field_ids = (
                Speech.objects.filter_valid_speeches(datetime.now())
                .filter(start_time__range=(from_timestamp, to_timestamp))
                .distinct("session__organizations")
                .values_list("session__organizations", flat=True)
            )
        playing_fields = Organization.objects.filter(id__in=playing_field_ids)
        for playing_field in playing_fields:
            save_sessions_tfidf_for_fresh_sessions(playing_field)
