import json
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from parlacards.solr import commit_to_solr, delete_from_solr
from parladata.models.legislation import Law


def delete_invalid_legislation(law_ids_in_solr):
    law_ids = list(Law.objects.all().values_list("id", flat=True))

    ids_to_delete = list(set(law_ids_in_solr) - set(law_ids))
    if bool(ids_to_delete):
        solr_ids_to_delete = ["law_" + str(i) for i in ids_to_delete]

        delete_from_solr(solr_ids_to_delete)


class Command(BaseCommand):
    help = "Uploads all legislation to solr"

    def handle(self, *args, **options):
        # get IDs from SOLR so we don't upload
        # law already there
        url = settings.SOLR_URL + "/select?wt=json&q=type:law&fl=law_id&rows=100000000"
        self.stdout.write(f"Getting all IDs from {url} ...")
        solr_response = requests.get(url)
        try:
            docs = solr_response.json()["response"]["docs"]
            ids_in_solr = [
                doc["law_id"]
                for doc in solr_response.json()["response"]["docs"]
                if "law_id" in doc
            ]
        except:
            ids_in_solr = []

        # delete invalid legislation
        self.stdout.write("Deleting invalid legislation ...")
        delete_invalid_legislation(ids_in_solr)
        yesterday = datetime.now() - timedelta(days=1)

        legislation = Law.objects.exclude(id__in=ids_in_solr).prefetch_related(
            "session"
        )
        updated_legislation = Law.objects.filter(
            updated_at__gte=yesterday
        ).prefetch_related("session")
        legislation = set(list(legislation) + list(updated_legislation))
        self.stdout.write(f"Uploading {len(legislation)} legislation to solr ...")
        output = []
        for i, law in enumerate(legislation):
            output.append(
                {
                    # WORKAROUND if law has not session then set mandat to 1
                    "term": law.mandate.id,
                    "type": "law",
                    "id": "law_" + str(law.id),
                    "law_id": law.id,
                    "session_id": law.session.id if law.session else None,
                    "start_time": law.timestamp.isoformat() if law.timestamp else None,
                    "content": law.text,
                }
            )

            if (i > 0) and (i % 100 == 0):
                commit_to_solr(self, output)
                output = []

        if bool(output):
            commit_to_solr(self, output)
