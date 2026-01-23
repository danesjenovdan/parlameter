import re
from datetime import datetime, timedelta
from string import punctuation

from django.conf import settings
from django.db.models import Max
from django.utils.module_loading import import_string

from parladata.models import Session


def get_dates_between(datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    number_of_days = (datetime_to - datetime_from).days

    return [(datetime_from + timedelta(days=i)) for i in range(number_of_days)]


def get_session_last_speech_dates(playing_field):
    """
    Get unique dates of last speeches of each session of which belong to playing_field organization.

    :param playing_field: Organization object representing the playing field
    """
    # Get the latest speech start_time for each session in one DB query
    end_dates = (
        Session.objects.filter(organizations=playing_field)
        .annotate(last_speech_time=Max("speeches__start_time"))
        .values_list("last_speech_time", flat=True)
    )

    # Convert to dates and remove None values
    end_dates = [dt.date() for dt in end_dates if dt is not None]

    # Return sorted unique dates
    return sorted(set(end_dates))


def get_fortnights_between(datetime_from=None, datetime_to=None):
    if not datetime_from:
        datetime_from = datetime.now()
    if not datetime_to:
        datetime_to = datetime.now()

    number_of_fortnights = (datetime_to - datetime_from).days % 14

    return [
        (datetime_from + timedelta(days=(i * 14))) for i in range(number_of_fortnights)
    ]


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", punctuation))


def tokenize(text):
    return [s for s in re.split(r"\s", text) if s != ""]


def get_lemmatize_method(name, language_code=None):
    """
    name: name of lemmatizer method for import
    """
    if not language_code:
        language_code = getattr(
            settings,
            "LEMMATIZER_LANGUAGE_CODE",
        )

    mathod_path_string = f"parlacards.lemmatizers.{language_code}.lemmatizer.{name}"
    method = import_string(mathod_path_string)
    return method
