import json
import os
import zipfile
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from parladata.models import (
    AgendaItem,
    Ballot,
    Document,
    Motion,
    Organization,
    Person,
    Session,
    Vote,
)
from parladata.models.common import Mandate
from parladata.update_utils import send_email


class Command(BaseCommand):
    help = "Run "

    def handle(self, *args, **options):
        documents = Document.objects.filter(tags__name="sentio").exclude(
            tags__name="parsed"
        )
        for document in documents:
            file_path = self.download_file(document.file)
            self.parse(file_path)
            print(file_path)
            document.tags.add("parsed")

    def parse(self, file_path):
        # workaround add zip extension
        os.rename(file_path, file_path + ".zip")
        # unzip file
        with zipfile.ZipFile(file_path + ".zip", "r") as zip_ref:
            zip_ref.extractall("data")
        f = open("data/package.json")
        data = json.load(f)
        people = {}
        for participant in data["participant"]:
            if participant["enabled"]:
                people[participant["no"]] = Person.objects.filter(
                    parser_names__icontains=participant["name"]
                ).first()

        print("loaded", people)

        errors = []

        session_type = data["export"]["session"]["type"]
        session_date = data["export"]["session"]["participantList"]["dateOfLastChange"]
        session_id = data["export"]["session"]["id"]

        start_time = datetime.fromisoformat(session_date.split("T")[0])

        mandate = Mandate.get_active_mandate_at(start_time)
        organization = mandate.query_root_organizations(start_time)[1]

        if Session.objects.filter(gov_id=session_id).exists():
            print(f"skip parsing {session_id}")
            return

        try:
            ai_order = AgendaItem.objects.latest("order").order
        except ObjectDoesNotExist:
            ai_order = 0

        agenda_items = {}
        votes = {}

        for item in data["element"]:
            start_time = item["startDate"]
            if item["type"] == "Session":
                session_name = item["name"]
                session = Session(
                    name=session_name,
                    classification=session_type.lower(),
                    start_time=start_time,
                    gov_id=session_id,
                    mandate=mandate,
                )
                session.save()
                session.organizations.add(organization)
            if item["type"] == "Group":
                ai_order += 1
                agenda_item = AgendaItem(
                    name=item["name"],
                    session=session,
                    datetime=start_time,
                    order=ai_order,
                )
                agenda_item.save()
                agenda_items[item["no"]] = agenda_item
            if item["type"] == "Item":
                motion = Motion(
                    datetime=start_time,
                    session=session,
                    text=item["description"],
                    title=item["description"],
                    result=None,
                )
                motion.save()
                if item["parentNo"]:
                    motion.agenda_items.add(agenda_items[item["parentNo"]])
                else:
                    errors.append(
                        f'Glasovanje {item["description"]} nima točke dnevnega reda'
                    )
                    print(f'Glasovanje {item["description"]} nima točke dnevnega reda')
                vote = Vote(
                    name=item["description"],
                    motion=motion,
                    timestamp=start_time,
                    result=None,
                )
                vote.save()
                votes[item["no"]] = vote

        for vote_item in data["voting"]:
            print(vote_item.keys())
            info = vote_item["ballot"]
            vote = votes[vote_item["elementNo"]]
            structure = info["structure"]
            options = {option["no"]: option["type"] for option in structure["option"]}
            vote.result = info["result"]["value"] == "Accepted"
            vote.save()
            motion = vote.motion
            motion.result = info["result"]["value"] == "Accepted"
            motion.save()
            for ballot in info["participant"]:
                Ballot(
                    vote=vote,
                    personvoter=people[ballot["participantNo"]],
                    option=self.get_option(ballot, options),
                ).save()

        if errors:
            editor_permission_group = Group.objects.filter(
                name__icontains="editor"
            ).first()
            for editor in editor_permission_group.user_set.all():
                print("Send error email to", editor.email)
                send_email(
                    _(
                        "Pri parsanju sentio datoteke smo naleteli na potencialne napake"
                    ),
                    editor.email,
                    "error_notification.html",
                    {
                        "base_url": settings.BASE_URL,
                        "errors": errors,
                        "session": session,
                    },
                )

    def get_option(self, ballot, options):
        if ballot["voted"]:
            return options[ballot["checkedOption"][0]].lower()
        elif ballot["present"]:
            return "abstain"
        else:
            return "absent"

    def download_file(self, file):
        if settings.PARLAMETER_ENABLE_S3:
            response = requests.get(file.url)
            file_path = f"parladata/data/{file.name}"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            return file.path
