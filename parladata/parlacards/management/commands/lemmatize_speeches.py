from django.core.management.base import BaseCommand, CommandError

from parladata.models.speech import Speech


class Command(BaseCommand):
    help = "Lemmatizes all speeches"

    def handle(self, *args, **options):
        speeches = Speech.objects.filter(lemmatized_content=None)
        speech_count = speeches.count()

        print(f"Lemmatizing {speech_count} speeches ...")

        for i, speech in enumerate(speeches):
            speech.lemmatize_and_save()

            if i % 10 == 0:
                print(f"Done with {i} speeches ...")

        print("Done.")
