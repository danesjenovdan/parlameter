import json
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from parlacards.solr import commit_to_solr, delete_from_solr
from parladata.models.agenda_item import AgendaItem


def delete_invalid_agenda_items(commander, agenda_item_ids_in_solr):
    valid_agenda_item_ids = list(AgendaItem.objects.all().values_list("id", flat=True))

    ids_to_delete = list(set(agenda_item_ids_in_solr) - set(valid_agenda_item_ids))

    solr_ids_to_delete = ["agenda_item_" + str(i) for i in ids_to_delete]
    commander.stdout.write(
        f"About to delete {len(solr_ids_to_delete)} agenda items from solr"
    )

    delete_from_solr(solr_ids_to_delete)


class Command(BaseCommand):
    help = "Uploads all agenda_items to solr"

    def handle(self, *args, **options):
        # get IDs from SOLR so we don't upload
        # agenda_items already there
        yesterday = datetime.now() - timedelta(days=1)
        url = (
            settings.SOLR_URL
            + "/select?wt=json&q=type:agenda_item&fl=agenda_item_id&rows=100000000"
        )
        self.stdout.write(f"Getting all IDs from {url} ...")
        solr_response = requests.get(url)
        try:
            docs = solr_response.json()["response"]["docs"]
            ids_in_solr = [
                doc["agenda_item_id"]
                for doc in solr_response.json()["response"]["docs"]
                if "agenda_item_id" in doc
            ]
        except:
            ids_in_solr = []

        # delete invalid agenda_items
        self.stdout.write("Deleting invalid agenda_items ...")
        delete_invalid_agenda_items(self, ids_in_solr)

        agenda_items = AgendaItem.objects.all().exclude(id__in=ids_in_solr)
        updated_agenda_items = (
            AgendaItem.objects.all()
            .filter(updated_at__gte=yesterday)
            .prefetch_related("session", "session__mandate")
        )
        agenda_items = set(list(agenda_items) + list(updated_agenda_items))
        self.stdout.write(f"Uploading {len(agenda_items)} agenda_items to solr ...")
        output = []
        for i, agenda_item in enumerate(agenda_items):
            if not agenda_item.session:
                continue
            output.append(
                {
                    "type": "agenda_item",
                    "id": "agenda_item_" + str(agenda_item.id),
                    "agenda_item_id": agenda_item.id,
                    "start_time": agenda_item.datetime.isoformat(),
                    "title": agenda_item.name,
                    "content": agenda_item.text,
                    "session_id": agenda_item.session.id,
                    "term": agenda_item.session.mandate.id,
                }
            )

            if (i > 0) and (i % 100 == 0):
                commit_to_solr(self, output)
                output = []

        if bool(output):
            commit_to_solr(self, output)
