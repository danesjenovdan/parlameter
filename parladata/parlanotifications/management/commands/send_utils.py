from datetime import datetime, timedelta
from itertools import groupby

import requests
from django.conf import settings
from django.utils.translation import gettext as _
from sentry_sdk import capture_message

from parlacards.solr import shorten_highlighted_content
from parladata.models import AgendaItem, Law, Speech, Vote
from parladata.update_utils import send_email
from parlanotifications.models import Keyword


def solr_select(
    text_query="*",
    date_from=None,
):
    document_type = "speech"
    fl = "speech_id"
    sort = "start_time desc"
    from_date = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")

    q_params = f"{text_query} AND type:{document_type}"
    q_params = f"{text_query}"
    fq_params = f"start_time:[{from_date} TO NOW]"

    params = {
        "wt": "json",
        "sort": sort,
        "rows": 500,
        "q": q_params,
        "fq": fq_params,
        # "fl": fl,
        "hl": "true",
        "hl.fl": "content",
        "hl.fragsize": 0,
        "hl.snippets": 1,
    }

    url = f"{settings.SOLR_URL}/select"

    # some failure modes handled
    # first, assuming that a response comes, we try
    try:
        response = requests.get(url, params=params, timeout=3)

        # "die" gracefully when Solr is reachable but "broken"
        if response.status_code >= 400:
            print(response.status_code)
            # if 404 or similar (also 5xx), just warn and return
            # an empty but structured response
            capture_message(
                f"Solr unreachable at {settings.SOLR_URL}. Error {response.status_code}.",
                level="warning",
            )
            return {
                "response": {
                    "docs": [],
                    "numFound": 0,
                }
            }
    except Exception as e:
        print(e)
        return {
            "response": {
                "docs": [],
                "numFound": 0,
            }
        }

    return response.json()


# data = solr_select(text_query="Zakon o pomoči pri prostovoljnem končanju življenja", date_from=datetime.now()-timedelta(days=30))


def send_notification_email(user, users_docs, keyword_ids, sending_date):
    print("send emails for user ", user.email)
    send_email(
        _("V državnem zboru je bila obravnavana izbrana tema"),
        user.email,
        "notification.html",
        {"data": users_docs, "uuid": user.uuid},
    )
    user.notification_sent_at = sending_date
    Keyword.objects.filter(id__in=keyword_ids).update(
        latest_notification_sent_at=sending_date
    )
    user.save()


def send_emails():
    sending_date = datetime.now().date()
    daily_keywords = Keyword.objects.filter(notification_frequency="DAILY").exclude(
        latest_notification_sent_at__gt=sending_date - timedelta(days=1)
    )

    weekly_keywords = Keyword.objects.filter(notification_frequency="WEEKLY").exclude(
        latest_notification_sent_at__gt=sending_date - timedelta(days=7)
    )

    monthly_keywords = Keyword.objects.filter(notification_frequency="MONTHLY").exclude(
        latest_notification_sent_at__gt=sending_date - timedelta(days=30)
    )

    keywords = daily_keywords.union(weekly_keywords).union(monthly_keywords)

    user_keywords = groupby(keywords, lambda keyword: keyword.user)

    for user, keywords in user_keywords:
        users_docs = {}
        keyword_ids = []
        for keyword in keywords:
            # narrow and wide search
            search_string = (
                keyword.keyword
                if keyword.matching_method == "WIDE"
                else f'"{keyword.keyword}"'
            )
            date_from = (
                keyword.latest_notification_sent_at
                if keyword.latest_notification_sent_at
                else datetime.now() - timedelta(days=30)
            )
            data = solr_select(text_query=search_string, date_from=date_from)
            if data["response"]["numFound"] > 0:
                print(data.keys())
                print(data["response"].keys())
                search_results = data["highlighting"]
                enriched_search_results = {
                    "speeches": [],
                    "agenda_items": [],
                    "votes": [],
                    "legislation": [],
                }
                for key, highlight in search_results.items():
                    splited_key = key.split("_")
                    print(splited_key)
                    if splited_key[0] == "speech":
                        speech = Speech.objects.get(id=splited_key[1])
                        enriched_search_results["speeches"].append(
                            {
                                "id": speech.id,
                                "content": shorten_highlighted_content(
                                    highlight["content"][0]
                                )
                                .replace("<em>", "<strong>")
                                .replace("</em>", "</strong>"),
                                "timestamp": speech.start_time,
                                "speaker_name": speech.speaker.name,
                                "session_name": get_session_name(speech.session),
                                "session_id": speech.session_id,
                                "order": int((speech.order - 1) / 10) + 1,
                                "type": "speech",
                            }
                        )
                    elif splited_key[0] == "agenda":
                        agenda_item = AgendaItem.objects.filter(
                            id=splited_key[2]
                        ).first()
                        enriched_search_results["agenda_items"].append(
                            {
                                "id": agenda_item.id,
                                "content": shorten_highlighted_content(
                                    highlight["content"][0]
                                )
                                .replace("<em>", "<strong>")
                                .replace("</em>", "</strong>"),
                                "timestamp": agenda_item.datetime,
                                "session_id": agenda_item.session_id,
                                "session_name": get_session_name(agenda_item.session),
                                "type": "agenda_item",
                            }
                        )
                    elif splited_key[0] == "vote":
                        vote = Vote.objects.filter(id=splited_key[1]).first()
                        enriched_search_results["votes"].append(
                            {
                                "id": vote.id,
                                "content": shorten_highlighted_content(
                                    highlight["content"][0]
                                )
                                .replace("<em>", "<strong>")
                                .replace("</em>", "</strong>"),
                                "timestamp": vote.motion.datetime,
                                "session_name": get_session_name(vote.motion.session),
                                "session_id": vote.motion.session_id,
                                "type": "vote",
                            }
                        )
                    elif splited_key[0] == "law":
                        law = Law.objects.filter(id=splited_key[1]).first()
                        enriched_search_results["legislation"].append(
                            {
                                "id": law.id,
                                "content": shorten_highlighted_content(
                                    highlight["content"][0]
                                )
                                .replace("<em>", "<strong>")
                                .replace("</em>", "</strong>"),
                                "timestamp": law.timestamp,
                                "type": "law",
                            }
                        )
                keyword_ids.append(keyword.id)
                users_docs[keyword] = enriched_search_results

        if users_docs:
            send_notification_email(user, users_docs, keyword_ids, sending_date)


def get_session_name(session):
    names = [org.name for org in session.organizations.all()]
    return f"{session.name} ({', '.join(names)})"
