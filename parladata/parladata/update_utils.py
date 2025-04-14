import operator
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from parlacards.models import SessionTfidf
from parladata.models.agenda_item import AgendaItem
from parladata.models.legislation import LegislationConsideration
from parladata.models.motion import Motion
from parladata.models.person import Person
from parladata.models.public_question import PublicPersonQuestion
from parladata.models.session import Session
from parladata.models.speech import Speech
from parladata.models.vote import Vote

"""
relativno navadno večino: (večina prisotnih poslancev; najpogostejši način odločanja),
absolutno navadno večino: (vsaj 46 glasov poslancev),
relativno kvalificirano večino: (2/3 prisotnih poslancev) ali
absolutno kvalificirano večino: (vsaj 60 glasov poslancev).
"""


def get_result_for_relative_normal_majority(vote):
    options = vote.get_option_counts()
    return options["for"] > options["against"]


def get_result_for_absolute_normal_majority(vote):
    options = vote.get_option_counts()
    return options["for"] > (sum(options.values()) / 2 + 1)


def set_results_to_votes(majority="relative_normal"):
    for vote in Vote.objects.filter(result=None):
        if majority == "absolute_normal":
            final_result = get_result_for_absolute_normal_majority(vote)
        else:
            final_result = get_result_for_relative_normal_majority(vote)

        motion = vote.motion
        motion.result = final_result
        motion.save()
        vote.result = final_result
        vote.save()


def pair_motions_with_speeches():
    for session in Session.objects.all():
        motions = session.motions.filter(speech=None)
        speeches_with_motion = session.speeches.filter(
            Q(content__contains="PROTI"), Q(content__contains="ZA")
        )
        contents = {speech.id: speech.content for speech in speeches_with_motion}
        for motion in motions:
            title = motion.title
            splitted_title = title.split(" ")
            scores = {}
            for speech_id, content in contents.items():
                score = 0.0
                for word in splitted_title:
                    if word in content:
                        score += 1
                scores[speech_id] = score / len(splitted_title)

            if scores:
                the_speech = max(scores.items(), key=operator.itemgetter(1))[0]
                speech = speeches_with_motion.get(id=the_speech)
                speech.motions.add(motion)
                score = scores[the_speech]
                speech.tags.add(str(int(score * 10) * 10))


def notify_editors_for_new_data():
    now = datetime.now()
    previous_parse = now - timedelta(hours=int(settings.PARSER_INTERVAL_HOURS))

    new_tfidf_sessions = [
        tfidf.session
        for tfidf in SessionTfidf.objects.filter(
            created_at__gte=previous_parse
        ).distinct("session")
    ]

    new_motions = Motion.objects.filter(created_at__gte=previous_parse)
    fresh_speeches = Speech.objects.filter(
        created_at__gte=previous_parse
    )  # first speeches batch of session
    new_speeches = Speech.objects.filter(
        created_at__gte=previous_parse
    )  # new speeches on session
    editor_permission_group = Group.objects.filter(name__icontains="editor").first()
    sessions = [
        speech.session
        for speech in new_speeches.distinct("session")
        if speech.session not in new_tfidf_sessions
    ]
    new_people = Person.objects.filter(created_at__gte=previous_parse)
    new_voters = Person.objects.filter(
        ballots__isnull=False, person_memberships__isnull=True
    ).distinct("id")
    new_legislation_considered = LegislationConsideration.objects.filter(
        created_at__gte=previous_parse
    )

    new_votes_need_editing = Vote.objects.filter(
        created_at__gte=previous_parse, needs_editing=True
    )

    assert bool(editor_permission_group), "There's no editor permission group"

    if (
        new_motions
        or new_speeches
        or new_people
        or fresh_speeches
        or new_legislation_considered
    ):
        for editor in editor_permission_group.user_set.all():
            send_email(
                _("New data for edit in parlameter ") + settings.INSTALATION_NAME,
                editor.email,
                "daily_notification.html",
                {
                    "base_url": settings.BASE_URL,
                    "new_motions": new_motions,
                    "new_speeches": new_speeches,
                    "sessions": sessions,
                    "new_tfidf_sessions": new_tfidf_sessions,
                    "new_voters": new_voters,
                    "new_people": new_people,
                    "new_votes_need_editing": new_votes_need_editing,
                    "new_legislation_considered": new_legislation_considered,
                    "instalation_name": settings.INSTALATION_NAME,
                },
            )


def send_email(
    subject, to_email, template, data, from_email=settings.FROM_EMAIL, reply_to=None
):
    cur_language = translation.get_language()
    if settings.EMAIL_LANGUAGE_CODE:
        translation.activate(settings.EMAIL_LANGUAGE_CODE)
    html_body = render_to_string(template, data)
    text_body = strip_tags(html_body)

    if not reply_to:
        reply_to = settings.FROM_EMAIL

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=from_email,
        to=[to_email],
        body=text_body,
        reply_to=[reply_to],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
    translation.activate(cur_language)


def set_vote_session(print_method=print):
    sessions = Session.objects.all().order_by("start_time")
    session_count = sessions.count()
    for idx, session in enumerate(sessions):
        start_time = session.start_time
        if idx + 1 < session_count:
            end_time = sessions[idx + 1].start_time
        else:
            end_time = datetime.max
        motions = Motion.objects.filter(
            datetime__gte=start_time,
            datetime__lte=end_time,
            session__isnull=True,
        )
        print_method(f"{motions.count()} motions updated with session.")
        motions.update(session=session)


def reset_order_on_speech():
    agenda_item_order = Subquery(
        AgendaItem.objects.filter(
            speeches=OuterRef("id"),
        )
        .order_by("order")
        .values("order")[:1]
    )
    now = datetime.now()
    previous_parse = now - timedelta(hours=settings.PARSER_INTERVAL_HOURS)
    with transaction.atomic():
        new_speeches = Speech.objects.filter(updated_at__gte=previous_parse)
    sessions = [s.session for s in new_speeches.distinct("session")]
    for session in sessions:
        print("update session: ", session)
        speeches = speeches.annotate(ai_order=agenda_item_order)
        speeches = (
            Speech.objects.filter(session=session)
            .annotate(ai_order=agenda_item_order)
            .order_by("ai_order", "id", "order", "id")
        )
        for i, speech in enumerate(speeches):
            speech.order = i + 1
            speech.save()
