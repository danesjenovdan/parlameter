import math
from datetime import datetime, timedelta

from django.conf import settings
from icu import Collator, Locale

from parladata.models.memberships import OrganizationMembership, PersonMembership

local_collator = Collator.createInstance(Locale(settings.LANGUAGE_CODE))


def get_playing_fields(timestamp):
    organization_memberships = (
        OrganizationMembership.valid_at(timestamp)
        .filter(member__classification="house")
        .distinct("member")
    )

    return [
        organization_membership.member
        for organization_membership in organization_memberships
    ]


def truncate_score(score):
    trunc_factor = 10**5
    try:
        score = math.trunc(score * trunc_factor) / trunc_factor
    except:
        score = 0
    return score


def process_month_string(month_string, min_year=None, max_year=None):
    try:
        year, month = map(lambda x: int(x), month_string.split("-"))
    except ValueError:
        return None, None

    if month < 1 or month > 12:
        return None, None

    if min_year and year < min_year:
        return None, None
    if max_year and year > max_year:
        return None, None

    return year, month


def month_tuple_to_datetime_range(month_tuple):
    if not month_tuple or not all(month_tuple) or len(month_tuple) != 2:
        return None, None
    year, month = month_tuple

    start_date = datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    end_date = datetime(
        year=next_year,
        month=next_month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - timedelta(microseconds=1)

    return start_date, end_date


def process_months_string(months_string, min_year=None, max_year=None):
    months = months_string.split(",") if months_string else []
    tuples = [process_month_string(month, min_year, max_year) for month in months]
    ranges = [month_tuple_to_datetime_range(month_tuple) for month_tuple in tuples]
    return [month_range for month_range in ranges if all(month_range)]
