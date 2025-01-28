from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from parlacards.serializers.vote import VoteSerializer
from parladata.models.vote import Vote


class Command(BaseCommand):
    help = "Caches all the votes if they are not already cached."

    def handle(self, *args, **options):
        for vote in Vote.objects.all():
            print(f"Caching vote with id {vote.id}")
            serializer = VoteSerializer(vote, context={"date": datetime.today(), "request_date": datetime.today()})
            # call serializer.data to actually cache everything
            serializer.data
