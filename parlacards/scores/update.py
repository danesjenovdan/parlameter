from parlacards.scores.attendance import save_people_vote_attendance, save_groups_vote_attendance
from parlacards.scores.avg_number_of_speeches_per_session import save_people_avg_number_of_speeches_per_session
from parlacards.scores.deviation_from_group import save_people_deviations_from_group
from parlacards.scores.discord import (
    save_groups_discords,
    save_organizations_vote_discords,
)
from parlacards.scores.monthly_attendance import save_people_monthly_vote_attendance, save_groups_monthly_vote_attendance
from parlacards.scores.number_of_questions import save_people_number_of_questions, save_group_number_of_questions
from parlacards.scores.number_of_spoken_words import save_people_number_of_spoken_words
from parlacards.scores.session_attendance import save_groups_vote_attendance_on_sessions
from parlacards.scores.vocabulary_size import save_people_vocabulary_sizes, save_groups_vocabulary_sizes
from parlacards.scores.voting_distance import save_voting_distances, save_groups_voting_distances
from parlacards.utils import get_playing_fields

from parladata.models.motion import Motion
from parladata.models.question import Question
from parladata.models.speech import Speech
from parladata.models.organization import Organization
from parladata.models.memberships import PersonMembership

from datetime import datetime, timedelta

def run_analyises_for_new_data(timestamp=None):
    if not timestamp:
        timestamp = datetime.now()

    from_timestamp = timestamp - timedelta(days=1)

    new_motions = Motion.objects.filter(created_at__gte=from_timestamp)
    new_speeches = Speech.objects.filter(created_at__gte=from_timestamp)
    new_questions = Question.objects.filter(created_at__gte=from_timestamp)

    motion_playing_fields = new_motions.distinct(
        "session__organizations"
    ).values_list(
        "session__organizations",
        flat=True
    )
    for playing_field in motion_playing_fields:
        if playing_field == None:
            continue
        playing_field = Organization.objects.get(id=playing_field)
        print(f'Running votes analyses for: {playing_field.name}')
        run_vote_analyses_on_date(playing_field, timestamp)

    speech_playing_fields = new_speeches.distinct(
        "session__organizations"
    ).values_list(
        "session__organizations",
        flat=True
    )

    for playing_field in speech_playing_fields:
        if playing_field:
            playing_field = Organization.objects.get(id=playing_field)
            print(f'Running speeches analyses for: {playing_field.name}')
            run_speech_analyses_on_date(playing_field, timestamp)

    # get playing fieds of question authors
    person_memberships_of_questions = PersonMembership.objects.filter(
        role='voter',
        member_id__in=new_questions.values_list("person_authors", flat=True)
    ).distinct('organization')

    question_playing_fields = [
        person_membership.organization
        for person_membership 
        in person_memberships_of_questions
    ]
    for playing_field in question_playing_fields:
        if playing_field:
            print(f'Running questions analyses for: {playing_field.name}')
            run_question_analyses_on_date(playing_field, timestamp)

def force_run_analyses(timestamp=None, print_method=print):
    if not timestamp:
        timestamp = datetime.now()


    for playing_field in get_playing_fields(timestamp):
        print(f'Runing analyses for: {playing_field.name}')
        print_method('start vote analyses')
        run_vote_analyses_on_date(playing_field, timestamp)
        print_method('start speech analyses')
        run_speech_analyses_on_date(playing_field, timestamp)
        print_method('start question analyses')
        run_question_analyses_on_date(playing_field, timestamp)
        print_method('finish')


def force_run_group_analyses(timestamp=None, print_method=print):
    if not timestamp:
        timestamp = datetime.now()

    print_method('start analyses for groups')
    for playing_field in get_playing_fields(timestamp):
        save_group_number_of_questions(playing_field, timestamp)
        save_groups_voting_distances(playing_field, timestamp)
        save_groups_monthly_vote_attendance(playing_field, timestamp)
        save_groups_vote_attendance_on_sessions(playing_field, timestamp)
        save_groups_discords(playing_field, timestamp)
        save_groups_vote_attendance(playing_field, timestamp)
        save_groups_vocabulary_sizes(playing_field, timestamp)

def force_run_person_analyses(timestamp=None, print_method=print):
    if not timestamp:
        timestamp = datetime.now()
    print_method('start analyses for people')
    for playing_field in get_playing_fields(timestamp):
        print_method('start calculating ang number of speeches')
        save_people_avg_number_of_speeches_per_session(playing_field, timestamp)
        print_method('start calculating number of spoken words')
        save_people_number_of_spoken_words(playing_field, timestamp)
        print_method('start calculating vocabulary size')
        save_people_vocabulary_sizes(playing_field, timestamp)
        print_method('start calculating attendace')
        save_people_vote_attendance(playing_field, timestamp)
        print_method('start calculating deviations from group')
        save_people_deviations_from_group(playing_field, timestamp)
        print_method('start calculating monthly vote attendance')
        save_people_monthly_vote_attendance(playing_field, timestamp)
        print_method('start calculating voting distances')
        save_voting_distances(playing_field, timestamp)
        print_method('start calculating number of questions')
        save_people_number_of_questions(playing_field, timestamp)
        print_method('end analyses for people')

def run_speech_analyses_on_date(playing_field, timestamp):
    save_people_avg_number_of_speeches_per_session(playing_field, timestamp)
    save_people_number_of_spoken_words(playing_field, timestamp)
    save_people_vocabulary_sizes(playing_field, timestamp)
    save_groups_vocabulary_sizes(playing_field, timestamp)


def run_vote_analyses_on_date(playing_field, timestamp):
    save_people_vote_attendance(playing_field, timestamp)
    save_groups_vote_attendance(playing_field, timestamp)
    save_people_deviations_from_group(playing_field, timestamp)
    save_groups_discords(playing_field, timestamp)
    save_organizations_vote_discords(playing_field, timestamp)
    save_people_monthly_vote_attendance(playing_field, timestamp)
    save_groups_monthly_vote_attendance(playing_field, timestamp)
    save_groups_vote_attendance_on_sessions(playing_field, timestamp)
    save_voting_distances(playing_field, timestamp)
    save_groups_voting_distances(playing_field, timestamp)

def run_question_analyses_on_date(playing_field, timestamp):
    save_people_number_of_questions(playing_field, timestamp)
    save_group_number_of_questions(playing_field, timestamp)
