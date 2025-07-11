from datetime import datetime

from django.core.management.base import BaseCommand

from parlacards.models import GroupUnity, PersonNumberOfSpokenWords
from parladata.models.common import Mandate
from parladata.models.memberships import OrganizationMembership, PersonMembership
from parladata.models.organization import Organization
from parladata.models.person import Person
from parladata.models.session import Session
from parladata.models.speech import Speech
from parladata.models.versionable_properties import OrganizationName, PersonName
from parladata.models.vote import Vote


class Command(BaseCommand):
    help = """
    Prepare database for tests (delete data)'

    * import_db.sh (import mol databse)
        * copy database
        * load database
    * python manage.py prepare_test_database
    * python manage.py migrate parlacards zero
    * python manage.py migrate
    * python manage.py run_all_analyses --start_time 2022-11-30
    * python manage.py run_all_analyses --start_time 2022-12-13
    * python manage.py dumpdata -e contenttypes -e auth.permission -o tests/fixtures/test_db.json
    """
    FAKE_PERSON_SOURCE_ID = 424

    def handle(self, *args, **options):
        # delete sessions
        Session.objects.all().exclude(id__in=[3783, 3782, 4280, 4283]).delete()

        mandate2 = Mandate.objects.get(id=2)

        mol2 = Organization.objects.get(id=48)
        sd = Organization.objects.get(id=19)
        svoboda = Organization.objects.get(id=52)

        # move sd memberships to another group for mandate 2
        PersonMembership.objects.filter(organization=sd, mandate=mandate2).update(
            organization=svoboda
        )
        PersonMembership.objects.filter(on_behalf_of=sd, mandate=mandate2).update(
            on_behalf_of=svoboda
        )
        OrganizationMembership.objects.filter(organization=mol2, member=sd).delete()

        # fix set mandate to existing organization memberships
        for root in OrganizationMembership.objects.filter(
            member__classification="root"
        ):
            OrganizationMembership.objects.filter(organization=root.member).update(
                mandate=root.mandate
            )

        Speech.objects.filter(session_id__in=[4280, 4283]).delete()

        # vote id 11094 contains only anonymous ballots
        Vote.objects.get(id=11094).ballots.all().update(personvoter=None)
        # vote id 11093 contains some anonymous ballots
        for ballot in Vote.objects.get(id=11093).ballots.all()[:15]:
            ballot.personvoter = None
            ballot.save()
        # vote id 11092 contains no ballots at all
        Vote.objects.get(id=11092).ballots.all().delete()

        # duplicate playing field (with session + data and memberships) for test bicameral systems
        root_membership_mandate_2 = OrganizationMembership.objects.get(id=30)
        root_membership_mandate_2.id = None
        second_mol_2 = root_membership_mandate_2.member
        second_mol_2.id = None
        second_mol_2.save()
        OrganizationName(value="Mestni svet Dom 2 2022-2026", owner=second_mol_2).save()
        second_mol_2.save()
        root_membership_mandate_2.member = second_mol_2
        root_membership_mandate_2.save()

        # fake person for testing bicameral systems
        fake_primc = Person.objects.get(id=self.FAKE_PERSON_SOURCE_ID)
        fake_primc.id = None
        fake_primc.save()
        PersonName(value="Fake Primc", owner=fake_primc).save()

        # fake organization for testing bicameral systems
        fake_vesna = Organization.objects.get(id=18)
        fake_vesna.id = None
        fake_vesna.save()
        OrganizationName(value="Fake vesna", owner=fake_vesna).save()
        original_vesna = Organization.objects.get(id=18)

        org_memberships_mol2 = OrganizationMembership.objects.filter(
            organization=mol2,
        )
        for org_mems in org_memberships_mol2:
            if org_mems.member == original_vesna:
                org_mems.member = fake_vesna
                org_mems.id = None
                org_mems.organization = second_mol_2
                org_mems.save()

        person_memberships = PersonMembership.objects.filter(
            mandate=mandate2, organization=mol2
        )
        for membership in person_memberships:
            membership.id = None
            membership.organization = second_mol_2
            if membership.member_id == self.FAKE_PERSON_SOURCE_ID:
                membership.member = fake_primc
                PersonMembership(
                    member=fake_primc,
                    organization=fake_vesna,
                    start_time=membership.start_time,
                ).save()
            if membership.on_behalf_of == original_vesna:
                membership.on_behalf_of = fake_vesna
            else:
                membership.on_behalf_of = None
            membership.save()

        sessions = Session.objects.filter(organizations=mol2)
        for session in sessions:
            motions = session.motions.all().defer(None)
            speeches = session.speeches.all().defer(None)
            questions = session.question_set.all().defer(None)
            session.id = None
            session.save()
            session.organizations.clear()
            session.organizations.add(second_mol_2)
            for motion in motions:
                vote = motion.vote.first()
                motion.id = None
                motion.session = session
                motion.save()
                ballots = vote.ballots.all().defer(None)
                vote.id = None
                vote.motion = motion
                vote.save()
                for ballot in ballots:
                    ballot.id = None
                    ballot.vote = vote
                    ballot.save()
                    if ballot.personvoter_id == self.FAKE_PERSON_SOURCE_ID:
                        ballot.personvoter = fake_primc
                        ballot.save()

            for speech in speeches:
                speech.id = None
                speech.session = session
                speech.save()
                if speech.speaker_id == self.FAKE_PERSON_SOURCE_ID:
                    speech.speaker = fake_primc
                    speech.save()

            for question in questions:
                question.id = None
                question.session = session
                question.save()
                if question.person_authors == self.FAKE_PERSON_SOURCE_ID:
                    question.person_authors.add(fake_primc)
