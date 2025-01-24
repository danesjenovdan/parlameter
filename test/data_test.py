from django.conf import settings
from django.db.models import Count

from parladata.models import Link, Motion, Session, Speech, Vote


def testDocumentsLinks():

    motionsWithoutLink = []

    motions = Motion.objects.all()
    for motion in motions:
        mCount = motion.links.all().count()
        if mCount == 0:
            motionsWithoutLink.append(motion.id)

    if motionsWithoutLink:
        print("Motions without documents: \n" + str(motionsWithoutLink))

    return "Test fail" if motionsWithoutLink else "Test pass"


def testDuplSpeeches():
    sk = Session.objects.filter(name__icontains="skupna seja")
    s = Speech.getValidSpeeches(datetime.now()).filter(session__in=sk)
    dups = (
        s.values("order", "speaker_id", "start_time")
        .annotate(count=Count("id"))
        .values("order", "speaker_id", "start_time")
        .order_by()
        .filter(count__gt=1)
    )
    duplications = []
    sessions = []
    for d in dups:
        multi = s.filter(
            start_time=d["start_time"], order=d["order"], speaker_id=d["speaker_id"]
        ).order_by("valid_from")

    duplications.append(multi.values_list("id"))
    dupl_session = list(multi.values_list("session_id"))
    dupl_session.sort()
    sessions.append(dupl_session)

    unique_pairs = [list(x) for x in set(tuple(x) for x in sessions)]

    if duplications:
        print("Speech duplications: \n" + str(duplications))

    return "Test fail" if motionsWithoutLink else "Test pass"


def speechesOnSessionTest():
    data = []
    for s in Session.objects.all().order_by("organization_id"):
        if not s.speeches.all():
            data.append(
                {
                    "id": s.id,
                    "date": s.start_time,
                    "name": s.name,
                    "org_name": s.organization.name,
                }
            )

    info_text = "Sessions without Speeches: \n"
    for s in data:
        info_text += str(s) + "\n"

    if data:
        print("Sessions without Speeches: \n" + mail_text)
