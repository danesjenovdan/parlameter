from parlacards.solr import delete_from_solr
from parladata.models import Organization, Person, Session


def merge_people(real_person_id, fake_person_ids, print_method=print):
    print_method("Real person id: %s" % real_person_id)
    print_method("Fake people ids: %s" % ", ".join(fake_person_ids))
    print_method("\n")

    # check if real person exists
    try:
        real_person = Person.objects.get(id=int(real_person_id))
    except Person.DoesNotExist:
        raise Exception("No real person found")

    # check if fake people exist
    if (
        Person.objects.filter(
            id__in=[int(person_id) for person_id in fake_person_ids]
        ).count()
        > 0
    ):
        fake_people = Person.objects.filter(
            id__in=[int(person_id) for person_id in fake_person_ids]
        )
    else:
        raise Exception("No fake people found")

    # deal with ballots
    print_method("Real person has %d ballots." % real_person.ballots.all().count())
    for fake_person in fake_people:
        print_method(
            "Fake person %d has %d ballots."
            % (fake_person.id, fake_person.ballots.all().count())
        )
        print_method("Moving ballots to real person...")
        for ballot in fake_person.ballots.all():
            ballot.personvoter = real_person
            ballot.save()
        print_method("Done with moving.")

    print_method("\n")

    edited_speech_ids = []

    print_method("Real person has %d speeches." % real_person.speeches.all().count())
    for fake_person in fake_people:
        print_method(
            "Fake person %d has %d speeches."
            % (fake_person.id, fake_person.speeches.all().count())
        )
        print_method("Moving speeches to real person...")
        for speech in fake_person.speeches.all():
            speech.speaker = real_person
            speech.save()
            edited_speech_ids.append("speech_" + str(speech.id))
        print_method("Done with moving.")
    if edited_speech_ids:
        delete_from_solr(edited_speech_ids)

    print_method(
        f"Real person is author of {real_person.authored_questions.all().count()} questions."
    )
    for fake_person in fake_people:
        print_method(
            f"Fake person {fake_person.id} is author of {fake_person.authored_questions.all().count()} questions."
        )
        print_method("Moving questions to real person...")
        for question in fake_person.authored_questions.all():
            question.person_authors.remove(fake_person)
            question.person_authors.add(real_person)
            question.save()
        print_method("Done with moving.")

    print_method(
        f"Real person is recipient of {real_person.received_questions.all().count()} questions."
    )
    for fake_person in fake_people:
        print_method(
            f"Fake person {fake_person.id} is recipient of {fake_person.received_questions.all().count()} questions."
        )
        print_method("Moving questions to real person...")
        for question in fake_person.received_questions.all():
            question.recipient_people.remove(fake_person)
            question.recipient_people.add(real_person)
            question.save()
        print_method("Done with moving.")

    for fake_person in fake_people:
        fake_parser_names = fake_person.parser_names.split("|")
        for fake_parser_name in fake_parser_names:
            real_person.add_parser_name(fake_parser_name)
        real_person.save()
        print_method(str(fake_person.delete()))

    print_method("\n")
    print_method("DONE")


def merge_organizations(real_org_id, fake_orgs_ids, print_method=print):
    print_method(f"Real organization id: {real_org_id}")
    print_method(f"Fake organization ids: {fake_orgs_ids}")
    print_method("\n")

    # check if real organization exists
    try:
        real_org = Organization.objects.get(id=int(real_org_id))
    except Organization.DoesNotExist:
        raise Exception("No real organization found")

    # check if fake organizations exist
    fake_organizations = Organization.objects.filter(
        id__in=[int(org_id) for org_id in fake_orgs_ids]
    )
    if not fake_organizations:
        raise Exception("No fake organization found")

    print_method(
        f"Real organization is author of {real_org.questions_org_author.all().count()} questions."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is author of {fake_org.questions_org_author.all().count()} questions."
        )
        print_method("Moving questions to real organization...")
        for question in fake_org.questions_org_author.all():
            question.organization_authors.remove(fake_org)
            question.organization_authors.add(real_org)
            question.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is recipient of {real_org.questions_org.all().count()} questions."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is recipient of {fake_org.questions_org.all().count()} questions."
        )
        print_method("Moving questions to real organization...")
        for question in fake_org.questions_org.all():
            question.recipient_organizations.remove(fake_org)
            question.recipient_organizations.add(real_org)
            question.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.personmemberships_children.all().count()} memberships."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.personmemberships_children.all().count()} memberships."
        )
        print_method("Moving membership to real organization...")
        for membership in fake_org.personmemberships_children.all():
            membership.organization = real_org
            membership.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is child of {real_org.organization_memberships.all().count()} organization memberships."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.organization_memberships.all().count()} memberships."
        )
        print_method("Moving membership to real organization...")
        for membership in fake_org.organization_memberships.all():
            membership.member = real_org
            membership.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.representatives.all().count()} representatives."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.representatives.all().count()} representatives."
        )
        print_method("Moving membership to real organization...")
        for membership in fake_org.representatives.all():
            membership.on_behalf_of = real_org
            membership.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.sessions.all().count()} sessions."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.sessions.all().count()} sessions."
        )
        print_method("Moving sessions to real organization...")
        for session in fake_org.sessions.all():
            session.organizations.remove(fake_org)
            session.organizations.add(real_org)
            session.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.laws.all().count()} legislation."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.laws.all().count()} legislation."
        )
        print_method("Moving membership to real organization...")
        for law in fake_org.laws.all():
            law.organization = real_org
            law.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.legislationconsideration_set.all().count()} legislation consideration."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.legislationconsideration_set.all().count()} legislation consideration."
        )
        print_method("Moving membership to real organization...")
        for legislationconsideration in fake_org.legislationconsideration_set.all():
            legislationconsideration.organization = real_org
            legislationconsideration.save()
        print_method("Done with moving.")

    print_method(f"Real organization is owner of {real_org.links.all().count()} links.")
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.links.all().count()} links."
        )
        print_method("Moving membership to real organization...")
        for link in fake_org.links.all():
            link.organization = real_org
            link.save()
        print_method("Done with moving.")

    print_method(
        f"Real organization is owner of {real_org.ballot_set.all().count()} ballots."
    )
    for fake_org in fake_organizations:
        print_method(
            f"Fake organization {fake_org.id} is owner of {fake_org.ballot_set.all().count()} ballots."
        )
        print_method("Moving membership to real organization...")
        fake_org.ballot_set.all().update(orgvoter=real_org)
        print_method("Done with moving.")

    for fake_org in fake_organizations:
        fake_org_names = fake_org.parser_names.split("|")
        for fake_org_name in fake_org_names:
            real_org.add_parser_name(fake_org_name)
        real_org.save()
        print_method(str(fake_org.delete()))


def merge_sessions(real_session_id, duplicated_session_id, print_method=print):
    print_method(f"Real session id: {real_session_id}")
    print_method(f"Duplicate session id: {duplicated_session_id}")
    print_method("\n")

    # check if real session exists
    try:
        real_session = Session.objects.get(id=int(real_session_id))
    except Session.DoesNotExist:
        raise Exception("No real session found")

    # check if duplicate sessions exist
    duplicated_session = Session.objects.filter(id=duplicated_session_id).first()
    if not duplicated_session:
        raise Exception("No duplicate session found")

    duplicate_speeches = duplicated_session.speeches.all()
    print_method(
        f"Delete {duplicate_speeches.count()} speeches from duplicate session."
    )
    duplicate_speeches.delete()

    duplicate_votes = duplicated_session.motions.all()
    print_method(f"Delete {duplicate_votes.count()} votes.")
    duplicate_votes.delete()

    real_session_through = real_session.session_organization_through.all()
    for rst in real_session_through:
        if not rst.name:
            rst.name = real_session.name
            rst.save()

    real_session.gov_id = f"{real_session.gov_id}|{duplicated_session.gov_id}"
    real_session.is_joint_session = True
    real_session.name = f"{real_session.name} ({real_session.organizations.first().name}), {duplicated_session.name} ({duplicated_session.organizations.first().name})"
    real_session.needs_editing = False
    real_session.save()

    duplicated_session_through = duplicated_session.session_organization_through.all()
    duplicated_session_through.update(
        session=real_session,
        name=duplicated_session.name,
    )

    print(duplicated_session.delete())
