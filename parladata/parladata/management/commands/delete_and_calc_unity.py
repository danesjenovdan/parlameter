from django.core.management.base import BaseCommand, CommandError

from parlacards.models import GroupUnity
from parlacards.scores.unity import save_organizations_vote_unities
from parladata.models.common import Mandate
from parladata.models.motion import Motion
from parladata.models.organization import (
    CLASSIFICATIONS as ORGANIZATION_CLASSIFICATIONS,
)
from parladata.models.organization import (
    Organization,
)


class Command(BaseCommand):
    help = "Delete all unity scores and recalculate them"

    def add_arguments(self, parser):
        parser.add_argument("mandate_id", type=int)

    def handle(self, *args, **options):
        mandate_id = options.get("mandate_id", None)
        if mandate_id:
            mandates = Mandate.objects.get(id=mandate_id)
        else:
            mandates = Mandate.objects.all()
        GroupUnity.objects.all().delete()
        self.stdout.write("Deleted all unity scores")
        for mandate in mandates:
            mandate_p = self.style.SUCCESS(f"{mandate}")
            self.stdout.write(f"Calculating unity scores for mandate {mandate_p}")

            from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(None)

            filtered_classifications = [
                c[0] for c in ORGANIZATION_CLASSIFICATIONS if c[0] != "pg"
            ]

            motion_organizations__ids = (
                Motion.objects.filter(datetime__range=(from_timestamp, to_timestamp))
                .filter(
                    session__organizations__classification__in=filtered_classifications
                )
                .values_list("session__organizations__id", flat=True)
                .distinct()
            )

            bodies = Organization.objects.filter(id__in=motion_organizations__ids)

            i = 0
            num = len(bodies)

            for body in bodies:
                i += 1
                body_p = self.style.SUCCESS(f"{body.id} ({body.name[:32]}...)")
                self.stdout.write(f"{i}/{num} | Calculating unity score for {body_p}")
                save_organizations_vote_unities(body)
