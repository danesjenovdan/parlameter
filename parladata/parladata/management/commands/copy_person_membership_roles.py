from django.core.management.base import BaseCommand, CommandError

from parladata.models.memberships import PersonMembership
from parladata.models.organization import Organization


class Command(BaseCommand):
    """
    Examples:
        - manage.py copy_person_membership_roles 402 voter --copy_from_roles all
        - manage.py copy_person_membership_roles 402 voter --copy_from_roles member deputy
    """

    help = (
        "Copy person membership in organization from one or more roles to another role."
    )

    def add_arguments(self, parser):
        parser.add_argument("org_id", type=int)
        parser.add_argument("new_role", type=str)
        parser.add_argument("--copy_from_roles", type=str, nargs="+", required=True)

    def handle(self, *args, **options):
        org_id = options["org_id"]
        new_role = options["new_role"]
        from_roles = options["copy_from_roles"]

        organization = Organization.objects.filter(id=options["org_id"]).first()
        if not organization:
            raise CommandError(f"Organization with id `{org_id}` does not exist")

        valid_roles = [role[0] for role in PersonMembership.ROLES]
        if new_role not in valid_roles:
            raise CommandError(f"Role `{new_role}` is not a valid role")

        valid_from_roles = [role for role in valid_roles if role != new_role]
        if len(from_roles) == 1 and from_roles[0] == "all":
            from_roles = valid_from_roles
        else:
            for role in from_roles:
                if role not in valid_from_roles:
                    if role == new_role:
                        raise CommandError(f"Role `{role}` is the same as the new role")
                    raise CommandError(f"Role `{role}` is not a valid role")

        org_p = self.style.SUCCESS(f"{org_id} ({organization.name[:32]}...)")
        role_p = self.style.SUCCESS(f"{new_role}")
        self.stdout.write(f"Updating organization {org_p} with new role {role_p}")
        self.stdout.write(f"Copying roles {from_roles}")

        memberships = PersonMembership.objects.filter(
            organization=organization, role__in=from_roles
        )
        for membership in memberships:
            existing = PersonMembership.objects.filter(
                start_time=membership.start_time,
                organization=organization,
                member=membership.member,
                role=new_role,
            ).first()
            if existing:
                self.stdout.write(
                    f"Role '{new_role}' already exists for person {membership.member.id} ({membership.member.name})"
                )
                continue

            self.stdout.write(
                f"Copying role '{membership.role}' -> '{new_role}' for person {membership.member.id} ({membership.member.name})"
            )
            PersonMembership.objects.create(
                member=membership.member,
                role=new_role,
                on_behalf_of=membership.on_behalf_of,
                start_time=membership.start_time,
                end_time=membership.end_time,
                organization=membership.organization,
                mandate=membership.mandate,
            )
