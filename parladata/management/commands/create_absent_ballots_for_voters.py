from importlib import import_module

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from parladata.models import Ballot, Organization, Vote


class Command(BaseCommand):
    help = "Run "

    def handle(self, *args, **options):
        orgs = Organization.objects.filter(
            personmemberships_children__role="voter"
        ).distinct("id")
        annotated_votes = Vote.objects.annotate(ballots_count=Count("ballots"))
        for org in orgs:
            voter_count = org.query_voters().count()
            votes = annotated_votes.filter(motion__session__organizations=org)
            # exclude votes with correct or zero ballots
            false_votes = votes.exclude(ballots_count=voter_count).exclude(
                ballots_count=0
            )
            for false_vote in false_votes:
                voters = org.query_voters(false_vote.motion.datetime)
                ballots = false_vote.ballots.all()
                if ballots[0].personvoter:
                    # add assigned ballots
                    active_voters = ballots.values_list("personvoter", flat=True)
                    absent_voters = voters.exclude(id__in=active_voters)
                    Ballot.objects.bulk_create(
                        [
                            Ballot(personvoter=voter, vote=false_vote, option="absent")
                            for voter in absent_voters
                        ]
                    )
                else:
                    # add anonymous ballots

                    Ballot.objects.bulk_create(
                        [
                            Ballot(vote=false_vote, option="absent")
                            for i in range(voters.count() - ballots.count())
                        ]
                    )
