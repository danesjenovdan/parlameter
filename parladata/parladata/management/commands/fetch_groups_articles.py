from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from eventregistry import *

from parladata.models.common import Mandate
from parladata.models.media import MediaReport, Medium


class Command(BaseCommand):
    help = "Merges people together"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            nargs="?",
            default="31",
            help="days ago range for fetching articles",
        )

    def handle(self, *args, **options):
        er = EventRegistry(apiKey=settings.ER_API_KEY)
        self.stdout.write("-" * 80)

        days = options["days"]

        mandate = Mandate.objects.first()
        playing_field = mandate.query_root_organizations()[1]
        groups = playing_field.query_parliamentary_groups()

        medium_uris = [medium.uri for medium in Medium.objects.filter(active=True)]
        self.stdout.write(f"Medium URIs: {medium_uris}")

        self.stdout.write(f"Parsing form {days} days ago")

        for group in groups:
            name = group.name

            self.stdout.write(f"Medium URIs: {medium_uris}")
            self.stdout.write("-" * 80)

            q = QueryArticlesIter(
                sourceUri=QueryItems.OR(medium_uris),
                keywords=name,
                dateStart=datetime.datetime.now() - datetime.timedelta(days=int(days)),
                isDuplicateFilter="skipDuplicates",
            )

            results = q.execQuery(er, sortBy="date")

            newEventsCount = 0
            newArticlesCount = 0

            for article in results:
                articleUrl = article.get("url", "")

                articleUri = article.get("uri", "")
                if MediaReport.objects.filter(
                    uri=articleUri, mentioned_organizations=group
                ).exists():
                    continue

                mediumUri = article.get("source", {}).get("uri")
                medium = Medium.objects.filter(uri=mediumUri).first()
                if not medium:
                    continue

                articleTitle = article.get("title", "")
                articleDateTime = article.get("dateTime", None)

                report = MediaReport.objects.filter(uri=articleUri).first()
                if not report:
                    report = MediaReport.objects.create(
                        title=articleTitle,
                        url=articleUrl,
                        uri=articleUri,
                        report_date=articleDateTime.split("T")[0],
                        medium=medium,
                    )

                report.mentioned_organizations.add(group)

                self.stdout.write(f"NEW ARTICLE: {articleUri} - {articleTitle}")
                newArticlesCount += 1

                self.stdout.write("-" * 80)

            self.stdout.write("-" * 80)
            self.stdout.write(f"+ new articles: {newArticlesCount}")
            self.stdout.write("-" * 80)
            self.stdout.write("+ DONE")
            self.stdout.write("-" * 80)
