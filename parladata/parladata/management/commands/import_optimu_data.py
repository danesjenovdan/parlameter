from collections import defaultdict
from datetime import datetime, timedelta

import requests
import xmltodict
from django.conf import settings
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from parladata.models import (
    AgendaItem,
    Ballot,
    Document,
    Motion,
    Organization,
    OrganizationMembership,
    Person,
    PersonMembership,
    PersonName,
    Session,
    Vote,
)
from parladata.models.common import Mandate
from parladata.models.versionable_properties import OrganizationName, PersonName

VOTE_OPTIONS = {"0": "abstain", "1": "for", "2": "against"}


class Command(BaseCommand):
    help = "Run "

    def handle(self, *args, **options):
        self.people = {}

        # self.create_memberships_from_xml()

        documents = Document.objects.filter(tags__name="Optimu").exclude(
            tags__name="parsed"
        )
        for document in documents:
            file_path = self.download_file(document.file)
            self.parse(file_path)
            document.tags.add("parsed")

        management.call_command(
            "set_votes_result", "--majority", "relative_normal", verbosity=0
        )

    def parse(self, file_path):

        with open(file_path, "rb") as data_file:
            self.data = xmltodict.parse(data_file, dict_constructor=dict)

        self.agenda_items = {}
        self.votes = {}
        self.conclusions = {}
        self.vote_participants = defaultdict(list)
        self.session = None
        self.start_time = None

        self.load_people()
        if self.parse_session():
            # session is successfully parsed
            pass
        else:
            return
        self.parse_agenda_items()
        self.parse_votes_and_ballots()
        self.add_absent_ballots()

    def create_memberships_from_xml(self, file_path="1_REDNA.xml"):
        """
        Run this only once to create memberships from xml file when parladata is empty
        """
        with open(file_path, "rb") as data_file:
            self.data = xmltodict.parse(data_file, dict_constructor=dict)

        mandate = Mandate.get_active_mandate_at(datetime.now())
        if not mandate:
            mandate = Mandate(
                description="Nov mandat, uredi podatke",
                beginning=datetime.now() - timedelta(days=30),
            )
            mandate.save()
        default, playing_field = mandate.query_root_organizations(datetime.now())
        if not default:
            default = Organization()
            default.save()
            OrganizationName(
                owner=default,
                value="default",
            ).save()
            playing_field = Organization(classification="root")
            playing_field.save()
            OrganizationName(
                owner=playing_field,
                value="Občina XXX",
            ).save()
            OrganizationMembership(
                member=playing_field, organization=default, mandate=mandate
            )

        for participant in self.data["NewDataSet"]["Participant"]:
            participant_name = f'{participant["FirstName"]} {participant["LastName"]}'
            person = Person.objects.filter(
                parser_names__icontains=participant_name
            ).first()
            if person:
                self.people[participant["DeviceID"]] = person
            else:
                person = Person()
                person.save()
                person.add_parser_name(participant_name)
                PersonName(owner=person, value=participant_name).save()

            group_name = participant["GroupShortName"]
            group = Organization.objects.filter(
                parser_names__icontains=group_name
            ).first()
            if group:
                pass
            else:
                group = Organization(classification="pg")
                group.save()
                group.add_parser_name(group_name)
                OrganizationName(
                    owner=group,
                    value=group_name,
                ).save()
                OrganizationMembership(
                    member=group, organization=playing_field, mandate=mandate
                ).save()

            PersonMembership(
                member=person, organization=group, role="member", mandate=mandate
            ).save()

            PersonMembership(
                member=person,
                on_behalf_of=group,
                organization=playing_field,
                role="voter",
                mandate=mandate,
            ).save()

    def load_people(self):
        for participant in self.data["NewDataSet"]["Participant"]:
            participant_name = f'{participant["FirstName"]} {participant["LastName"]}'
            person = Person.objects.filter(
                parser_names__icontains=participant_name
            ).first()
            if person:
                self.people[participant["DeviceID"]] = person
            else:
                person = Person()
                person.save()
                person.add_parser_name(participant_name)
                PersonName(owner=person, value=participant_name).save()
                self.people[participant["DeviceID"]] = person

    def parse_session(self):
        session_name = self.data["NewDataSet"]["SessionInfo"]["Name"]
        if "redna" in session_name.lower():
            session_type = "regular"
        elif "izredna" in session_name.lower():
            session_type = "irregular"
        elif "nujna" in session_name.lower():
            session_type = "urgent"
        else:
            session_type = "unknown"

        session_id = self.data["NewDataSet"]["SessionInfo"]["Name"]
        self.start_time = datetime.fromisoformat(
            self.data["NewDataSet"]["SessionInfo"]["Created"].split(".")[0]
        ).date()

        mandate = Mandate.get_active_mandate_at(self.start_time)
        organization = mandate.query_root_organizations(self.start_time)[1]

        if Session.objects.filter(gov_id=session_id).exists():
            print(f"skip parsing {session_name}")
            return False
        else:
            self.session = Session(
                name=session_name,
                classification=session_type.lower(),
                start_time=self.start_time,
                gov_id=session_id,
                mandate=mandate,
            )
            self.session.save()
            self.session.organizations.add(organization)

        return True

    def parse_agenda_items(self):
        ai_order = 0
        try:
            ai_order = AgendaItem.objects.latest("order").order
        except ObjectDoesNotExist:
            ai_order = 0

        if isinstance(self.data["NewDataSet"]["PointOfDiscussion"], dict):
            self.data["NewDataSet"]["PointOfDiscussion"] = [
                self.data["NewDataSet"]["PointOfDiscussion"]
            ]
        for point in self.data["NewDataSet"]["PointOfDiscussion"]:
            description = point.get("Description", "").strip()
            description_items = description.split("\n\n")
            if len(description_items) == 3:
                title = description_items[1]
            else:
                title = description
            ai_order += 1
            agenda_item = AgendaItem(
                name=title,
                session=self.session,
                datetime=self.start_time,
                order=ai_order,
                text="",
            )
            agenda_item.save()
            self.agenda_items[point["PointOfDiscussionID"]] = agenda_item

        # update agenda items with conclusions
        if isinstance(self.data["NewDataSet"]["Conclusion"], dict):
            self.data["NewDataSet"]["Conclusion"] = [
                self.data["NewDataSet"]["Conclusion"]
            ]
        for conclusion in self.data["NewDataSet"]["Conclusion"]:
            this_agenda_item = self.agenda_items[conclusion["PointOfDiscussionID"]]
            if this_agenda_item.text:
                this_agenda_item.text += "\n\n"
            this_agenda_item.text += conclusion["Name"].strip()
            this_agenda_item.text += "\n"
            this_agenda_item.text += conclusion["Description"].strip()
            this_agenda_item.save()

            self.conclusions[conclusion["ConclusionID"]] = this_agenda_item

    def parse_votes_and_ballots(self):
        # registration ???
        for registration in self.data["NewDataSet"]["Registration"]:
            pass
        for participant_registration in self.data["NewDataSet"][
            "ParticipantRegistration"
        ]:
            pass

        # Motion and Vote
        if isinstance(self.data["NewDataSet"]["Session"], dict):
            self.data["NewDataSet"]["Session"] = [self.data["NewDataSet"]["Session"]]
        for xml_session in self.data["NewDataSet"]["Session"]:
            name = xml_session.get("CopyParticipantRegistrationObjectName", None)
            if not name:
                continue
            start_time = datetime.fromisoformat(
                xml_session["SessionVoteStartTime"].split(".")[0]
            )
            agenda_item = self.conclusions[xml_session["ConclusionID"]]
            motion = Motion(
                datetime=start_time,
                session=self.session,
                text=name,
                title=name,
                result=None,
            )
            motion.save()
            motion.agenda_items.add(agenda_item)
            vote = Vote(name=name, motion=motion, timestamp=start_time, result=None)
            vote.save()

            self.votes[xml_session["SessionID"]] = vote

        for xml_ballot in self.data["NewDataSet"]["SessionData"]:
            option = VOTE_OPTIONS[xml_ballot["Response"]]
            person = self.people[xml_ballot["DeviceID"]]
            vote = self.votes[xml_ballot["SessionID"]]
            registered = xml_ballot["Registered"]
            if option == "abstain" and registered == "false":
                option = "absent"
            Ballot(vote=vote, personvoter=person, option=option).save()
            self.vote_participants[xml_ballot["SessionID"]].append(person)

    def add_absent_ballots(self):
        for vote_id, participants in self.vote_participants.items():
            missing = set(self.people.values()).difference(participants)
            vote = self.votes[vote_id]
            for person in missing:
                Ballot(vote=vote, personvoter=person, option="absent").save()

    def download_file(self, file):
        if settings.PARLAMETER_ENABLE_S3:
            response = requests.get(file.url)
            file_path = f"parladata/data/{file.name}"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            return file.path
