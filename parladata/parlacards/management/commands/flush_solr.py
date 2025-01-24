from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from parlacards.solr import delete_solr_documents


class Command(BaseCommand):
    help = "Delete all documents from solr"

    def handle(self, *args, **options):
        delete_solr_documents()
