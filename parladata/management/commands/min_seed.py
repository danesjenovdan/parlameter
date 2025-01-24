import os
import uuid
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import Application

from parladata.models import (
    Area,
    Ballot,
    Law,
    LegislationStatus,
    Mandate,
    Motion,
    Organization,
    OrganizationMembership,
    Person,
    PersonMembership,
    Question,
    Session,
    Speech,
    Vote,
)
from parladata.models.versionable_properties import *
from parladata.models.versionable_properties import PersonName


class Command(BaseCommand):
    help = "Download croatian database"

    def handle(self, *args, **options):
        self.stdout.write("\n")
        self.stdout.write("Setting minimal setup")
        start_time = datetime(day=1, month=1, year=2020)

        bd = datetime(day=1, month=1, year=1968)

        area = Area(name="Center", classification="district")
        area.save()

        dz = Organization(classification="dz")
        dz.save()
        OrganizationName(value="DZ", owner=dz).save()
        OrganizationAcronym(value="DZ", owner=dz).save()

        coalition = Organization(
            classification="coalition",
        )
        coalition.save()
        OrganizationName(value="Coalition", owner=coalition).save()
        OrganizationAcronym(value="coal", owner=coalition).save()

        opposition = Organization(
            classification="opposition",
        )
        opposition.save()
        OrganizationName(value="Opposition", owner=opposition).save()
        OrganizationAcronym(value="opp", owner=opposition).save()

        coal_party = Organization(
            gov_id="13",
            classification="pg",
        )
        coal_party.save()
        coal_party.add_parser_name("Party from coalition")
        OrganizationName(value="Party from coalition", owner=coal_party).save()
        OrganizationAcronym(value="PFC", owner=coal_party).save()

        oppo_party = Organization(
            gov_id="12",
            classification="pg",
        )
        oppo_party.save()
        oppo_party.add_parser_name("Party from opposition")
        OrganizationName(value="Party from opposition", owner=oppo_party).save()
        OrganizationAcronym(value="PFO", owner=oppo_party).save()

        OrganizationMembership(
            member=coal_party, organization=dz, start_time=start_time
        ).save()
        OrganizationMembership(
            member=oppo_party, organization=dz, start_time=start_time
        ).save()

        OrganizationMembership(
            member=coal_party, organization=coalition, start_time=start_time
        ).save()

        OrganizationMembership(
            member=oppo_party, organization=opposition, start_time=start_time
        ).save()

        person_pfc_1 = Person(
            # name='Ivan Coalition',
            # previous_occupation='CEO',
            # education='Master of economics',
            # education_level=8,
            # number_of_mandates=3,
            # preferred_pronoun='he',
            date_of_birth=bd,
            # number_of_voters=100
        )
        person_pfc_1.save()
        person_pfc_1.districts.add(area)
        person_pfc_1.add_parser_name("Ivan Coalition")
        # add name
        person_pfc_1_name = PersonName(value="Ivan Coalition", owner=person_pfc_1)
        person_pfc_1_name.save()
        # add previous_occupation
        person_pfc_1_previous_occupation = PersonPreviousOccupation(
            value="CEO", owner=person_pfc_1
        )
        person_pfc_1_previous_occupation.save()
        # add education
        person_pfc_1_education = PersonEducation(
            value="Master of economics", owner=person_pfc_1
        )
        person_pfc_1_education.save()
        # add education level
        person_pfc_1_education_level = PersonEducationLevel(
            # TODO: fix
            # value=8,
            owner=person_pfc_1
        )
        person_pfc_1_education_level.save()
        # add number of mandates
        person_pfc_1_number_of_mandates = PersonNumberOfMandates(
            value=3, owner=person_pfc_1
        )
        person_pfc_1_number_of_mandates.save()
        # add number of voters
        person_pfc_1_number_of_voters = PersonNumberOfVoters(
            value=100, owner=person_pfc_1
        )
        person_pfc_1_number_of_voters.save()
        # add preferred pronoun
        person_pfc_1_preferred_pronoun = PersonPreferredPronoun(
            value="he", owner=person_pfc_1
        )
        person_pfc_1_preferred_pronoun.save()

        person_pfc_2 = Person(
            # name='Marjeta Coalition',
            # previous_occupation='CTO',
            # education='PhD',
            # education_level=9,
            # number_of_mandates=1,
            # preferred_pronoun='she',
            date_of_birth=bd,
            # number_of_voters=200
        )
        person_pfc_2.save()
        person_pfc_2.districts.add(area)
        person_pfc_2.add_parser_name("Marjeta Coalition")
        # add name
        person_pfc_2_name = PersonName(value="Marjeta Coalition", owner=person_pfc_2)
        person_pfc_2_name.save()
        # add previous_occupation
        person_pfc_2_previous_occupation = PersonPreviousOccupation(
            value="CTO", owner=person_pfc_2
        )
        person_pfc_2_previous_occupation.save()
        # add education
        person_pfc_2_education = PersonEducation(value="PhD", owner=person_pfc_2)
        person_pfc_2_education.save()
        # add education level
        person_pfc_2_education_level = PersonEducationLevel(
            # TODO: fix
            # value=9,
            owner=person_pfc_2
        )
        person_pfc_2_education_level.save()
        # add number of mandates
        person_pfc_2_number_of_mandates = PersonNumberOfMandates(
            value=1, owner=person_pfc_2
        )
        person_pfc_2_number_of_mandates.save()
        # add number of voters
        person_pfc_2_number_of_voters = PersonNumberOfVoters(
            value=100, owner=person_pfc_2
        )
        person_pfc_2_number_of_voters.save()
        # add preferred pronoun
        person_pfc_2_preferred_pronoun = PersonPreferredPronoun(
            value="she", owner=person_pfc_2
        )
        person_pfc_2_preferred_pronoun.save()

        person_pfo_1 = Person(
            # name='Maja Oppostion',
            # previous_occupation='MTM',
            # education='???',
            # education_level=7,
            # number_of_mandates=1,
            # preferred_pronoun='she',
            date_of_birth=bd,
            # number_of_voters=300
        )
        person_pfo_1.save()
        person_pfo_1.districts.add(area)
        person_pfo_1.add_parser_name("Maja Oppostion")
        # add name
        person_pfo_1_name = PersonName(value="Maja Opposition", owner=person_pfo_1)
        person_pfo_1_name.save()
        # add previous_occupation
        person_pfo_1_previous_occupation = PersonPreviousOccupation(
            value="MTM", owner=person_pfo_1
        )
        person_pfo_1_previous_occupation.save()
        # add education
        person_pfo_1_education = PersonEducation(value="???", owner=person_pfo_1)
        person_pfo_1_education.save()
        # add education level
        person_pfo_1_education_level = PersonEducationLevel(
            # TODO: fix
            # value=7,
            owner=person_pfo_1
        )
        person_pfo_1_education_level.save()
        # add number of mandates
        person_pfo_1_number_of_mandates = PersonNumberOfMandates(
            value=1, owner=person_pfo_1
        )
        person_pfo_1_number_of_mandates.save()
        # add number of voters
        person_pfo_1_number_of_voters = PersonNumberOfVoters(
            value=300, owner=person_pfo_1
        )
        person_pfo_1_number_of_voters.save()
        # add preferred pronoun
        person_pfo_1_preferred_pronoun = PersonPreferredPronoun(
            value="she", owner=person_pfo_1
        )
        person_pfo_1_preferred_pronoun.save()

        PersonMembership(
            role="voter",
            member=person_pfc_1,
            organization=dz,
            on_behalf_of=coal_party,
            start_time=start_time,
        ).save()

        PersonMembership(
            role="voter",
            member=person_pfc_2,
            organization=dz,
            on_behalf_of=coal_party,
            start_time=start_time,
        ).save()

        PersonMembership(
            role="voter",
            member=person_pfo_1,
            organization=dz,
            on_behalf_of=oppo_party,
            start_time=start_time,
        ).save()

        PersonMembership(
            role="president",
            member=person_pfc_1,
            organization=coal_party,
            on_behalf_of=None,
            start_time=start_time,
        ).save()

        PersonMembership(
            role="deputy",
            member=person_pfc_2,
            organization=coal_party,
            on_behalf_of=None,
            start_time=start_time,
        ).save()

        PersonMembership(
            role="president",
            member=person_pfo_1,
            organization=oppo_party,
            on_behalf_of=None,
            start_time=start_time,
        ).save()

        seed_mandate = Mandate(description="Seed mandate")
        seed_mandate.save()

        session = Session(
            name="Session 1.",
            start_time=start_time,
            in_review=False,
            mandate=seed_mandate,
        )
        session.save()
        session.organizations.add(dz)

        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_1,
            start_time=start_time + timedelta(minutes=5),
            order=1,
            session=session,
        ).save()
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_2,
            start_time=start_time + timedelta(minutes=15),
            order=2,
            session=session,
        ).save()
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfc_1,
            start_time=start_time + timedelta(minutes=25),
            order=3,
            session=session,
        ).save()
        Speech(
            content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            speaker=person_pfo_1,
            start_time=start_time + timedelta(minutes=35),
            order=4,
            session=session,
        ).save()

        motion = Motion(
            text="Voting for president",
            datetime=start_time,
            session=session,
            result="1",
        )
        motion.save()
        vote = Vote(
            name="Voting for president",
            motion=motion,
            timestamp=start_time + timedelta(minutes=35),
            result="1",
        )
        vote.save()

        Ballot(vote=vote, personvoter=person_pfc_1, option="for").save()
        Ballot(vote=vote, personvoter=person_pfc_2, option="for").save()
        Ballot(vote=vote, personvoter=person_pfo_1, option="against").save()

        question = Question(
            session=session,
            timestamp=start_time,
            answer_timestamp=start_time,
            title="Why we need to work on the first day?",
            recipient_text="Prime minister",
        )
        question.save()
        question.person_authors.add(person_pfo_1)

        Law(
            session=session,
            text="Voting for president",
            epa="EPA-1",
            classification="act",
            status="enacted",
            passed=True,
            timestamp=start_time,
        ).save()
        Law(
            session=session,
            text="Voting for dinner.",
            epa="EPA-1",
            classification="act",
            status="in_procedure",
        ).save()

        user = User(
            first_name="parlauser",
            username="parlauser",
            email="test@test.com",
            is_active=True,
            is_superuser=True,
            is_staff=True,
        )
        user.save()
        user.set_password("password")
        user.save()

        Application(
            client_id="kIZWxeodL29mfaKSIGQWPUuuck8CXv3m58XuJ8Y7",
            client_secret="54pWmrpj1y9FiwkUDofjeP4B5tbLQ4wW6F2wqsMT3JuQN4ApIqcveKlzOC1laQIJp8JpVi99EheHCkumEJ0o81J9f2uHK3eXjUdxprzDnWlsTuZM6cgv1Eo35KSr7Mfg",
            user=user,
            client_type="confidential",
            authorization_grant_type="password",
            name="client",
        ).save()

        LegislationStatus(name="in_procedure").save()
        LegislationStatus(name="received").save()
        LegislationStatus(name="adopted").save()
        LegislationStatus(name="retracted").save()
        LegislationStatus(name="rejected").save()
        LegislationStatus(name="submitted").save()
        LegislationStatus(name="enacted").save()
