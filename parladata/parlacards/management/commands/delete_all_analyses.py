from django.core.management.base import BaseCommand

from parlacards.models import *

ALL_MODELS = [
    VotingDistance,
    GroupVotingDistance,
    PersonAvgSpeechesPerSession,
    AgreementWithGroup,
    PersonNumberOfQuestions,
    PersonMonthlyVoteAttendance,
    GroupMonthlyVoteAttendance,
    GroupNumberOfQuestions,
    PersonVoteAttendance,
    GroupVoteAttendance,
    PersonStyleScore,
    GroupStyleScore,
    PersonNumberOfSpokenWords,
    PersonTfidf,
    GroupTfidf,
    SessionTfidf,
    SessionGroupAttendance,
    GroupDiscord,
    Quote,
    GroupUnity,
]


class Command(BaseCommand):
    help = "Deletes all analyses"

    def handle(self, *args, **options):
        for model in ALL_MODELS:
            model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted all analyses."))
