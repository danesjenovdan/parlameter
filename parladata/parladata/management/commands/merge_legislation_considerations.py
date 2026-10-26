from django.core.management.base import BaseCommand
from django.db import models, transaction

from parladata.models.legislation import LegislationConsideration

# Organization is unreliable in the source data, so it is not used to decide
# whether two considerations are duplicates.
MERGE_FIELDS = ["timestamp", "session_id"]


def filled_count(consideration):
    return sum(
        1
        for f in MERGE_FIELDS + ["organization_id"]
        if getattr(consideration, f) is not None
    )


def is_compatible(primary, other):
    """Compatible when no field has two different non-empty values."""
    for f in MERGE_FIELDS:
        a, b = getattr(primary, f), getattr(other, f)
        if a is not None and b is not None and a != b:
            return False
    return True


class Command(BaseCommand):
    help = (
        "Merges duplicated legislation considerations (same legislation and "
        "procedure phase) into the one with the most data, keeping all links."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print what would be merged.",
        )
        parser.add_argument(
            "--legislation",
            type=int,
            help="Only process considerations of the legislation with this id.",
        )
        parser.add_argument(
            "--mandate",
            type=int,
            help="Only process considerations of legislations in the mandate with this id.",
        )

        parser.add_argument(
            "--priority-organizations",
            type=int,
            nargs="*",
            default=[],
            help="Organization ids preferred when merging (e.g. the National Assembly ids of all mandates).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        self.priority_orgs = set(options["priority_organizations"])
        queryset = LegislationConsideration.objects.all()
        if options["legislation"] is not None:
            queryset = queryset.filter(legislation_id=options["legislation"])
        if options["mandate"] is not None:
            queryset = queryset.filter(legislation__mandate_id=options["mandate"])
        groups = (
            queryset.order_by()
            .values("legislation", "procedure_phase")
            .annotate(count_id=models.Count("id"))
            .filter(count_id__gt=1)
        )
        merged = 0
        conflicts = 0
        for group in groups:
            self.stdout.write(
                f"Processing group: legislation {group['legislation']}, phase {group['procedure_phase']}"
            )
            considerations = sorted(
                LegislationConsideration.objects.filter(
                    legislation=group["legislation"],
                    procedure_phase=group["procedure_phase"],
                ),
                key=lambda c: (
                    -filled_count(c),
                    c.organization_id not in self.priority_orgs,
                    c.id,
                ),
            )
            # Most complete first; each one joins a compatible primary or becomes a new one.
            primaries = []
            for consideration in considerations:
                target = next(
                    (p for p in primaries if is_compatible(p, consideration)), None
                )
                if target is None:
                    if primaries:
                        conflicts += 1
                        self.stdout.write(
                            f"Conflict, keeping separate: consideration {consideration.id} "
                            f"(legislation {group['legislation']}, phase {group['procedure_phase']})"
                        )
                    primaries.append(consideration)
                    continue
                self.stdout.write(
                    f"Merging consideration {consideration.id} into {target.id} "
                    f"(legislation {group['legislation']}, phase {group['procedure_phase']})"
                )
                merged += 1
                if not dry_run:
                    with transaction.atomic():
                        self.merge(target, consideration)
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would merge' if dry_run else 'Merged'} {merged}, conflicts left: {conflicts}"
            )
        )

    def merge(self, primary, duplicate):
        changed = False
        if duplicate.organization_id in self.priority_orgs and (
            primary.organization_id not in self.priority_orgs
        ):
            primary.organization_id = duplicate.organization_id
            changed = True
        elif primary.organization_id is None:
            primary.organization_id = duplicate.organization_id
            changed = primary.organization_id is not None
        for f in MERGE_FIELDS:
            if getattr(primary, f) is None and getattr(duplicate, f) is not None:
                setattr(primary, f, getattr(duplicate, f))
                changed = True
        if changed:
            primary.save()

        # Links with an url already on primary are redundant; the rest are moved.
        existing_urls = set(primary.links.values_list("url", flat=True))
        duplicate.links.exclude(url__in=existing_urls).update(
            legislation_consideration=primary
        )
        duplicate.delete()
