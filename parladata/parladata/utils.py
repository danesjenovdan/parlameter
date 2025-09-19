# -*- coding: utf-8 -*-
import csv
import importlib
import operator
import re
from collections import Counter
from datetime import datetime, timedelta
from functools import reduce

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.encoding import smart_str

from parladata.models import (
    Ballot,
    Mandate,
    Motion,
    Organization,
    OrganizationMembership,
    Person,
    PersonMembership,
    Session,
    Speech,
    Vote,
)
from parladata.models.agenda_item import AgendaItem
from parladata.models.task import Task


def AverageList(list):
    """Returns average from list of integers."""

    return sum(list) / float(len(list))


def AverageListOfDic(list, key):
    """Returns average from dictionary of integers."""

    data = [i[key] for i in list]
    return sum(data) / float(len(list))


def MaxListOfDic(list, key):
    """Returns maximum of list of dictionaries."""

    data = [i[key] for i in list]
    return max(data)


def getMPVoteObjects(date_=None):
    """Return objects of all parlament memberships with voting ability.
    Function: git config
    """

    if not date_:
        date_ = datetime.now()

    members = PersonMembership.objects.filter(role="voter").exclude(on_behalf_of=None)
    members = members.filter(
        Q(start_time__date__lte=date_) | Q(start_time=None),
        Q(end_time__date__gte=date_) | Q(end_time=None),
    ).prefetch_related("person")

    return members


def getCurrentMandate():
    """Returns current mandate."""

    return Mandate.objects.all()[-1]


def voteToLogical(vote):
    """Returns 1 instead of 'za' and 0 of 'proti'."""

    if vote == "for":
        return 1
    elif vote == "against":
        return 0
    else:
        return -1


# TODO this should be changed into a test
def getFails(organization):
    """Function for finding MPs membersihp date issues."""

    members = Membership.objects.filter(
        organization=organization, role="voter"
    ).exclude(on_behalf_of=None)

    start = Vote.objects.all().order_by("start_time")[0].start_time
    out = {}
    for member in members:
        if member.start_time is None and member.end_time is None:
            votes = Vote.objects.filter(
                Q(start_time__gte=start) | Q(end_time__lte=datetime.now())
            )
        elif member.start_time is None and member.end_time is not None:
            votes = Vote.objects.filter(
                Q(start_time__gte=start) | Q(end_time__lte=member.end_time)
            )
        elif member.start_time is not None and member.end_time is not None:
            votes = Vote.objects.filter(
                Q(start_time__gte=member.start_time) | Q(end_time__lte=member.end_time)
            )
        elif member.start_time is not None and member.end_time is None:
            votes = Vote.objects.filter(
                Q(start_time__gte=member.start_time) | Q(end_time__lte=datetime.now())
            )
        for vote in votes:
            if not Ballot.objects.filter(voter=member.person, vote=vote):
                if member.person.id in list(out.keys()):
                    out[member.person.id].append(vote.start_time)
                else:
                    out[member.person.id] = [vote.start_time]
    print(out)


# TODO this should be changed into a test
def getPersonWithoutVotes(organization):
    """Returns all MPs without votes."""

    members = PersonMembership.objects.filter(
        organization=organization, role="voter"
    ).exclude(on_behalf_of=None)

    with open("poor_voters.csv", "wb") as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        for vote in Vote.objects.all():
            real_voters = vote.ballots.all().values_list("voter__id", flat=True)
            fi_voters_memberships = members.filter(
                Q(start_time__lte=vote.start_time) | Q(start_time=None),
                Q(end_time__gte=vote.start_time) | Q(end_time=None),
            )
            fi_voters = fi_voters_memberships.values_list("person__id", flat=True)

            personWithoutVotes = list(set(fi_voters) - set(real_voters))

            mems = fi_voters_memberships.filter(person__id__in=personWithoutVotes)
            for personMem in mems:
                csvwriter.writerow(
                    [
                        vote.start_time,
                        personMem.id,
                        personMem.person.id,
                        personMem.person.name,
                    ]
                )


def postMembersFixer(request):
    """Fixes post of PGs."""

    context = {}
    context["posts"] = []
    for member in PersonMembership.objects.all():
        posts = member.memberships.all().order_by("start_time")
        start_time = member.start_time
        firstpost = member.memberships.filter(start_time=start_time)
        line = {"member": member, "fails": []}
        if not posts:
            line["fails"].append({"type": "empty"})
        elif firstpost:
            posts = posts.exclude(start_time=None)
            if posts.count() == 0:
                if firstpost[0].end_time != member.end_time:
                    line["fails"].append(
                        {
                            "type": "fail",
                            "note": "sam post z None start_timeom je in endtime se ne matcha z membershipom",
                            "posts": posts,
                        }
                    )
                continue
            # There is a post which start on membership start time
            if posts[0] == firstpost:
                temp_end = posts[0].end_time
                for post in list(posts)[1:]:
                    if post.start_time > temp_end + timedelta(days=2):
                        line["fails"].append(
                            {
                                "type": "fail",
                                "note": "Med posti je luknja",
                                "posts": posts,
                            }
                        )
                if list(posts)[-1].end_time != membership.end_time:
                    line["fails"].append(
                        {"type": "fail", "note": "endtime ni ok", "posts": posts}
                    )
        else:
            line["fails"].append(
                {"type": "fail", "note": "start_time je neki cudn", "posts": posts}
            )
        context["posts"].append(line)

    return render(request, "post.html", context)


def checkSessions(request, date_=None):
    """Returns number of sessions adjust to organization."""

    allSessoins = requests.get(
        "https://data.parlameter.si/v1/getSessions/" + date_
    ).json()
    ses = []
    mot = []
    for s in Organization.objects.all():
        session = requests.get(
            "https://data.parlameter.si/v1/getSessionsOfOrg/" + str(s.id) + "/" + date_
        ).json()
        for m in session:
            motionOfSession = requests.get(
                "https://data.parlameter.si/v1/motionOfSession/" + str(m["id"])
            ).json()
            mot.append({"Ime seje": m["name"], "St. glasovanj": len(motionOfSession)})
        ses.append({"Ime organizacije": s.name, "St. sej": len(session), "Seje": mot})
        mot = []
    out = {"DZ": {"Število sej": len(allSessoins), "Po org": ses}}
    return JsonResponse(out)


def membersFlowInOrg(request):
    """
    Debug method which shows when members joins and leave oragnizations.
    """
    context = {}
    context["orgs"] = []
    orgs_all = requests.get(
        "https://data.parlameter.si/v1/getOrganizatonsByClassification"
    ).json()
    orgs = [org["id"] for org in orgs_all["working_bodies"] + orgs_all["council"]]
    for org in orgs:
        flow = []
        org_id = org
        print(org)
        pgRanges = requests.get(
            "https://data.parlameter.si/v1/getMembersOfOrgsRanges/"
            + str(org_id)
            + "/"
            + datetime.now().strftime("%d.%m.%Y")
        ).json()
        for pgRange in pgRanges:
            count = len(
                [member for pg in list(pgRange["members"].values()) for member in pg]
            )
            members_ids = [
                member for pg in list(pgRange["members"].values()) for member in pg
            ]
            flow.append(
                {
                    "count": {
                        "count": count,
                        "start_date": pgRange["start_date"],
                        "end_date": pgRange["end_date"],
                    },
                    "members": [
                        member
                        for pg in list(pgRange["members"].values())
                        for member in pg
                    ],
                }
            )
            if len(flow) > 1:
                flow[-1]["added"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else ""
                        ),
                    }
                    for x in flow[-1]["members"]
                    if x not in flow[-2]["members"]
                ]
                flow[-1]["removed"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                end_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                    - timedelta(days=1)
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                end_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                    - timedelta(days=1)
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else None
                        ),
                    }
                    for x in flow[-2]["members"]
                    if x not in flow[-1]["members"]
                ]
                context["allMps"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else x
                        ),
                    }
                    for x in flow[-1]["members"]
                ]
            else:
                flow[-1]["added"] = [
                    {"name": Person.objects.get(id=x).name, "person_id": x}
                    for x in flow[-1]["members"]
                ]
        try:
            context["orgs"].append(
                {
                    "name": Organization.objects.get(id=org_id).name,
                    "flow": flow,
                    "allMps": context["allMps"],
                }
            )
        except:
            context["orgs"].append(
                {
                    "name": "ID: " + str(org_id),
                    "flow": flow,
                    "allMps": context["allMps"],
                    "allMps": context["allMps"],
                }
            )
    return render(request, "org_memberships.html", context)


def membersFlowInPGs(request):
    """
    Debug method which shows when members joins and leave partys.
    """
    context = {}
    context["orgs"] = []
    orgs_all = requests.get(
        "http://data.nov.parlameter.si/v1/getOrganizatonsByClassification"
    ).json()
    orgs = [org["id"] for org in orgs_all["parliamentary_groups"]]
    for org in orgs:
        flow = []
        org_id = org
        print(org)
        pgRanges = requests.get(
            "http://data.nov.parlameter.si/v1/getMembersOfPGsRanges/"
            + str(org_id)
            + "/"
            + datetime.now().strftime("%d.%m.%Y")
        ).json()
        for pgRange in pgRanges:
            count = len(
                [member for pg in list(pgRange["members"].values()) for member in pg]
            )
            members_ids = [
                member for pg in list(pgRange["members"].values()) for member in pg
            ]
            flow.append(
                {
                    "count": {
                        "count": count,
                        "start_date": pgRange["start_date"],
                        "end_date": pgRange["end_date"],
                    },
                    "members": [
                        member
                        for pg in list(pgRange["members"].values())
                        for member in pg
                    ],
                }
            )
            if len(flow) > 1:
                flow[-1]["added"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else ""
                        ),
                    }
                    for x in flow[-1]["members"]
                    if x not in flow[-2]["members"]
                ]
                flow[-1]["removed"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                end_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                    - timedelta(days=1)
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                end_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                    - timedelta(days=1)
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else None
                        ),
                    }
                    for x in flow[-2]["members"]
                    if x not in flow[-1]["members"]
                ]
                context["allMps"] = [
                    {
                        "name": Person.objects.get(id=x).name,
                        "membership": (
                            PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )[0]
                            if PersonMembership.objects.filter(
                                organization__id=org_id,
                                person__id=x,
                                start_time=(
                                    datetime.strptime(
                                        flow[-1]["count"]["start_date"], "%d.%m.%Y"
                                    )
                                ).strftime("%Y-%m-%d %H:%M"),
                            )
                            else x
                        ),
                    }
                    for x in flow[-1]["members"]
                ]
            else:
                flow[-1]["added"] = [
                    {"name": Person.objects.get(id=x).name, "person_id": x}
                    for x in flow[-1]["members"]
                ]
        try:
            context["orgs"].append(
                {
                    "name": Organization.objects.get(id=org_id).name,
                    "flow": flow,
                    "allMps": context["allMps"],
                }
            )
        except:
            context["orgs"].append(
                {
                    "name": "ID: " + str(org_id),
                    "flow": flow,
                    "allMps": context["allMps"],
                }
            )
    return render(request, "org_memberships.html", context)


def updateSpeechOrg():
    """Updates all speeches."""

    members = requests.get("https://data.parlameter.si/v1/getMembersOfPGsRanges").json()
    for mem in members:
        edate = datetime.strptime(mem["end_date"], settings.API_DATE_FORMAT)
        sdate = datetime.strptime(mem["start_date"], settings.API_DATE_FORMAT)
        speeches = Speech.objects.filter(
            start_time__range=[sdate, edate + timedelta(hours=23, minutes=59)]
        )
        print("count range speeches", speeches.count())
        for spee in speeches:
            for m, ids in list(mem["members"].items()):
                if spee.speaker.id in ids:
                    spee.party = Organization.objects.get(id=int(m))
                    spee.save()


def updateMotins():
    """Updates motion."""

    for motion in Motion.objects.all():
        yes = dict(
            Counter(
                Ballot.objects.filter(vote__motion=motion).values_list(
                    "option", flat=True
                )
            )
        ).get("for", 0)
        against = dict(
            Counter(
                Ballot.objects.filter(vote__motion=motion).values_list(
                    "option", flat=True
                )
            )
        ).get("against", 0)
        kvorum = dict(
            Counter(
                Ballot.objects.filter(vote__motion=motion).values_list(
                    "option", flat=True
                )
            )
        ).get("abstain", 0)
        no = dict(
            Counter(
                Ballot.objects.filter(vote__motion=motion).values_list(
                    "option", flat=True
                )
            )
        ).get("absent", 0)
        if (
            motion.title == "Dnevni red v celoti"
            or motion.title == "Širitev dnevnega reda".decode("utf8")
        ):
            if yes > (yes + against + kvorum + no) / 2:
                motion.result = 1
                motion.save()
            else:
                motion.result = 0
                motion.save()


def exportTagsOfVotes():
    """Exports all tags of all votes."""

    with open("tagged_votes.csv", "w") as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        votes = Vote.objects.all()
        for vote in votes:
            if vote.tags.all():
                print(
                    vote.session.name,
                    vote.motion.title,
                    vote.tags.all().values_list("name", flat=True),
                )
                csvwriter.writerow(
                    [
                        str(vote.session.name),
                        str(vote.motion.title),
                        str(";".join(vote.tags.all().values_list("name", flat=True))),
                    ]
                )
    return 1


def exportResultOfVotes():
    """Exports results of votes."""

    with open("result_of_votes.csv", "w") as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        votes = Motion.objects.all()
        count = 0
        for vote in votes:
            csvwriter.writerow(
                [str(vote.session.name), str(vote.text), str(vote.result)]
            )
            if vote.result:
                count += 1
    return 1


def migrateVotesInMotions():
    """Migrates objects Votes to Motion."""

    for vote in Motion.objects.filter(
        created_at__gte=(datetime.now() - timedelta(minutes=60))
    ):
        org = vote.session.organization
        session_name = vote.session.name
        ses = Session.objects.filter(
            name=session_name,
            created_at__lte=(datetime.now() - timedelta(minutes=60)),
            organization=org,
        )
        vote.session = ses[0]
        vote.save()
        print(ses[0].name, ses[0].created_at, vote.created_at)


def showSpeechesDuplicate():
    """Return all deplicated speeches."""

    def showData(qverySet, f):
        if len(list(set(list(qverySet.values_list("session_id", flat=True))))) > 1:
            f.write(qverySet[0].content)
            f.write(qverySet[0].speaker.name)
            f.write(qverySet[0].session.organization.name)

            f.write(
                "imajo isti cas"
                if len(list(set(list(qverySet.values_list("start_time", flat=True)))))
                < 2
                else "razlicen cas"
            )
            f.write(
                str(len(list(set(list(qverySet.values_list("start_time", flat=True))))))
                + " "
                + str(len(qverySet.values_list("start_time", flat=True)))
            )
            f.write(str(list(qverySet.values_list("session_id"))))
            f.write(str(list(qverySet.values_list("session__name"))))
            f.write(str(list(qverySet.values_list("session__organization__name"))))
            f.write("")

    ds = (
        Speech.objects.values("content")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    cl = [d["content"] for d in ds]
    f = open("duplicates.txt", "w")

    for content in cl:
        speeches = Speech.objects.filter(content=content)
        speakers = (
            speeches.values("speaker_id")
            .annotate(Count("id"))
            .order_by()
            .filter(id__count__gt=1)
        )
        for speaker in speakers:
            showData(speeches.filter(speaker_id=speaker["speaker_id"]), f)
    c.close()


def updateSessionInReviewStatus(filename):
    """Updates in review status of sessions."""

    with open(filename, "rb") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in spamreader:
            for candidate in row:
                id_session = None
                try:
                    id_session = int(candidate)
                except:
                    print("ni id :)", candidate)
                if id_session:
                    session = Session.objects.filter(id=id_session)
                    if session.count() == 1:
                        print("updejtam", session[0].name, "ivan")
                        session[0].in_review = True
                        session[0].save()
                    else:
                        print("Neki ni ql s sejo count je : ", session.count())


def determineSession(date_):
    """Returns session of DZ (redna seja) on given date."""

    fdate = datetime.strptime(date_, "%d.%m.%Y")
    toDate = fdate + timedelta(hours=23, minutes=59)
    session = Session.objects.filter(
        start_time__gte=fdate,
        start_time__lte=toDate,
        organization__id=95,
        name__icontains="redna",
    )
    if session:
        return session[0]
    else:
        return None


def determinePerson(full_name):
    """Checks if the person is in the attribute name_parser."""

    person = Person.objects.filter(name_parser__icontains=full_name)
    if person:
        return person[0]
    else:
        return None


def getIdSafe(obj):
    """Returns ID of object if exists."""

    if obj:
        return obj.id
    else:
        None


def replace_all(text, dic):
    """Replace all words in text attribute
    with the words in dic attribute.
    """

    for i, j in dic.items():
        pattern = re.compile(i, re.IGNORECASE)
        text = pattern.sub(j, text)
    return text


def jointSessionDataFix():
    ss = Session.objects.all()
    for s in ss:
        s.organizations.add(s.organization)


def deleteMotionsWithoutText():
    Motion.objects.filter(text="").delete()


def parseRecipient(text, date_of):
    # set utf-8 encoding
    import sys

    importlib.reload(sys)
    sys.setdefaultencoding("UTF-8")

    mv = Organization.objects.filter(
        classification__in=["vlada", "ministrstvo", "sluzba vlade", "urad vlade"]
    )
    out = []
    orgs = mv.values("_name", "id")
    data = {org["_name"].replace(",", ""): org for org in orgs}
    rts = text.split(", ")
    for rt in rts:
        role = None
        added = False
        text = ""
        if "minister" in rt:
            text = rt.split("minister ")[1]
            text = text.split(" v funkciji")[0]
        elif "ministrica" in rt:
            text = rt.split("ministrica ")[1]
            text = text.split(" v funkciji")[0]
        elif "predsednik Vlade" in rt:
            text = "Vlada"
            text = text.split(" v funkciji")[0]
            role = ["predsednik", "predsednica"]
        elif "Vlada" in rt:
            out.append({"recipient": mv.get(_name="Vlada"), "type": "org"})
            continue
        elif "generaln" in rt and "sekretar" in rt and "Vlade" in rt:
            text = "Vlada"
            text = text.split(" v funkciji")[0]
            role = ["generalni sekretar", "generalna sekretarka"]

        if text:
            # edge cases or fails on government page
            if "za razvoj strateške projekte in kohezijo" in text:
                text = "vlade za razvoj in evropsko kohezijsko politiko"
            elif "za Slovence v zamejstvu in po svetu" in text:
                text = "Urad vlade za Slovence v zamejstvu in po svetu"
            elif "infrastrukturo in prostor" in text:
                text = "za okolje in prostor"
            for d in data:
                if text in d:
                    org = mv.get(id=data[d]["id"])
                    posts = org.posts.filter(
                        Q(start_time__lte=date_of) | Q(start_time=None),
                        Q(end_time__gte=date_of) | Q(end_time=None),
                    )
                    if not posts:
                        posts = org.posts.filter(start_time__gte=date_of).order_by(
                            "start_time"
                        )
                    if role:
                        posts = posts.filter(role__in=role).order_by("start_time")
                    if posts:
                        out.append(
                            {"recipient": posts[0].membership.person, "type": "person"}
                        )
                        out.append({"recipient": posts[0], "type": "post"})
                        added = True
                    else:
                        print("There is no POsts", text, date_of)
                    break
                else:
                    pass

        if not added:
            out.append(None)
    return out


def parsePager(request, objs, default_per_page=1000):
    if request.GET:
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", default_per_page))
    else:
        page = 1
        per_page = default_per_page

    per_page = int(per_page)
    paginator = Paginator(objs, per_page)

    try:
        out = paginator.page(page)
    except PageNotAnInteger:
        out = paginator.page(1)
    except EmptyPage:
        out = paginator.page(paginator.num_pages)
    return out, {"page": page, "per_page": per_page, "pages": paginator.num_pages}


def hasNumbersOrPdfOrEndWord(inputString):
    end_words = ["PZE", "PZ", "P.Z.E."]
    has_number = any(char.isdigit() for char in inputString)
    has_pdf = "pdf" in inputString
    is_end_word = inputString in end_words
    return has_number or has_pdf or is_end_word


def make_person_merge_statistics(real_person_id, fake_person_ids):
    data = {}

    real_person = Person.objects.get(id=int(real_person_id))
    data["real_person"] = {
        "name": real_person.name,
        "ballots": real_person.ballots.all().count(),
        "speeches": real_person.speeches.all().count(),
        "authored_questions": real_person.authored_questions.all().count(),
        "received_questions": real_person.received_questions.all().count(),
    }

    data["fake_people"] = []

    fake_people = Person.objects.filter(id__in=fake_person_ids)
    print(fake_people)

    for fake_person in fake_people:
        data["fake_people"].append(
            {
                "name": fake_person.name,
                "ballots": fake_person.ballots.all().count(),
                "speeches": fake_person.speeches.all().count(),
                "authored_questions": fake_person.authored_questions.all().count(),
                "received_questions": fake_person.received_questions.all().count(),
            }
        )

    return data


def make_organization_merge_statistics(real_organization_id, fake_organization_ids):
    data = {}

    real_organization = Organization.objects.get(id=int(real_organization_id))
    data["real_organization"] = {
        "name": real_organization.name,
        "authored_questions": real_organization.questions_org_author.all().count(),
        "received_questions": real_organization.questions_org.all().count(),
    }

    data["fake_organizations"] = []

    fake_organizations = Organization.objects.filter(id__in=fake_organization_ids)
    print(fake_organizations)

    for fake_org in fake_organizations:
        data["fake_organizations"].append(
            {
                "name": fake_org.name,
                "authored_questions": fake_org.questions_org_author.all().count(),
                "received_questions": fake_org.questions_org.all().count(),
            }
        )

    return data


def move_votes(from_ai, to_ai):
    from_ai = AgendaItem.objects.get(id=from_ai)
    to_ai = AgendaItem.objects.get(id=to_ai)

    motions = from_ai.motions.all()
    for motion in motions:
        motion.agenda_items.clear()
        motion.agenda_items.add(to_ai)

    from_ai.save()
    to_ai.save()


def fix_agenda_items(fake_ai, true_ai, other_ai):
    faker = AgendaItem.objects.get(id=fake_ai)
    true_ai = AgendaItem.objects.get(id=true_ai)
    other_ai = AgendaItem.objects.get(id=other_ai)

    print(faker)
    print(true_ai)
    print(other_ai)

    move_votes(true_ai, other_ai)
    move_votes(faker, true_ai)
    faker.save()
    true_ai.save()
    other_ai.save()


def move_links(fake_ai, true_ai):
    faker = AgendaItem.objects.get(id=fake_ai)
    true_ai = AgendaItem.objects.get(id=true_ai)
    links = faker.links.all()
    links.update(agenda_item=true_ai)
    faker.save()
    true_ai.save()


# end all person memberships on specific date
def end_all_memberships(end_time):
    PersonMembership.objects.filter(end_time=None).update(end_time=end_time)
    OrganizationMembership.objects.filter(end_time=None).update(end_time=end_time)


# create new memberships in root organization from vote ballots
# copy memberships in parlamentary groups from previous mandate for old members starts on specific date
# create memberships for people without membership on PG to specific PG on specific date
def set_person_memberships_in_root_organization_from_vote(
    new_root_org, old_root_org, new_default_org, vote, start_time, mandate
):
    orgs = []
    for ballot in vote.ballots.all():
        person = ballot.personvoter
        old_org = None
        old_role = None
        old_membership = PersonMembership.objects.filter(
            organization=old_root_org, member=person, role="voter"
        )
        if old_membership:
            print(old_membership)
            old_membership = old_membership.latest("start_time")
            old_org = old_membership.on_behalf_of
            try:
                old_membership = PersonMembership.objects.filter(
                    organization=old_membership.on_behalf_of, member=person
                ).latest("start_time")
                old_role = old_membership.role
            except:
                pass
        else:
            old_org = new_default_org
            old_role = "member"
        orgs.append(old_org)
        PersonMembership(
            member=person,
            organization=new_root_org,
            start_time=start_time,
            on_behalf_of=old_org,
            mandate=mandate,
            role="voter",
        ).save()
        if old_org:  # for unaligned members
            PersonMembership(
                member=person,
                organization=old_org,
                start_time=start_time,
                role=old_role,
            ).save()

    for org in set(orgs):
        OrganizationMembership(
            organization=new_root_org, member=org, start_time=start_time
        ).save()


def start_slovenia_IX():
    # TODO: create Organization and mandate
    new_default_org = Organization.objects.get(id=138)
    new_root_org = Organization.objects.get(id=137)
    old_root_org = Organization.objects.get(id=1)
    vote = Vote.objects.get(id=6042)
    start_time = datetime(day=13, month=5, year=2022, hour=0, minute=1)
    end_all_memberships(start_time)
    set_person_memberships_in_root_organization_from_vote(
        new_root_org,
        old_root_org,
        new_default_org,
        vote,
        start_time + timedelta(minutes=1),
        Mandate.objects.last(),
    )


def merge_orgs():
    visited_ids = []
    orgs = Organization.objects.all().order_by("id")
    for org in orgs:
        if org.name == "Državni zbor":
            continue
        fakes = orgs.filter(parser_names__icontains=org.name).exclude(id=org.id)
        if visited_ids:
            fakes = fakes.exclude(id__in=visited_ids)
        visited_ids.append(org.id)
        if fakes:
            print(org.name)
            for fake in fakes:
                print(fake.name)
                visited_ids.append(fake.id)

            Task(
                name="merge_organizations",
                payload={
                    "real_org_id": org.id,
                    "fake_orgs_ids": list(fakes.values_list("id", flat=True)),
                },
                module_name="parladata.tasks",
                email_msg="test",
            ).save()
            print()


def delete_overlayed_memberships():
    m_member = PersonMembership.objects.all().distinct("member")
    for member in m_member:
        print(member.member)
        for o_member in PersonMembership.objects.filter(member=member.member).distinct(
            "organization"
        ):
            memberships = PersonMembership.objects.filter(
                member=o_member.member, organization=o_member.organization
            ).exclude(role="voter")
            visited = []
            for membership in memberships.order_by("start_time"):
                visited.append(membership.id)
                if membership.end_time:
                    united_memberships = (
                        memberships.filter(start_time__lte=membership.end_time)
                        .exclude(id__in=visited)
                        .exclude(role="voter")
                    )
                    if united_memberships:
                        print(membership.organization)
                        united_memberships.delete()

                else:
                    next_memberships = (
                        memberships.filter()
                        .exclude(id__in=visited)
                        .exclude(role="voter")
                    )
                    if next_memberships:
                        next_memberships
                        print(membership.organization)
                        next_memberships.delete()
        print()


def fix_playing_fields_mandates():
    for root in OrganizationMembership.objects.filter(member__classification="house"):
        OrganizationMembership.objects.filter(organization=root.member).update(
            mandate=root.mandate
        )
