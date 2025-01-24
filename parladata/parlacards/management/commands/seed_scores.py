from django.core.management.base import BaseCommand, CommandError

from parlacards.scores.seed import calculate_sparse_scores
from parladata.models.organization import Organization


class Command(BaseCommand):
    help = "Seeds sparse scores"

    def add_arguments(self, parser):
        parser.add_argument("main_org_id", type=int)

    def handle(self, *args, **options):
        main_organization = Organization.objects.get(id=options["main_org_id"])

        calculate_sparse_scores(main_organization)
