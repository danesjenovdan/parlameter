from itertools import chain
from importlib import import_module
from datetime import timedelta, datetime

from django.core.paginator import Paginator
from django.core.cache import cache

from django.db.models import Q, Count, Max
from django.db.models.functions import TruncDay

from rest_framework import serializers

from parladata.models.agenda_item import AgendaItem
from parladata.models.ballot import Ballot
from parladata.models.media import MediaReport
from parladata.models.vote import Vote
from parladata.models.question import Question
from parladata.models.memberships import PersonMembership
from parladata.models.legislation import Law
from parladata.models.question import Question
from parladata.models.speech import Speech
from parladata.models.organization import Organization
from parladata.models.person import Person
from parladata.models.common import Mandate
from parladata.models.public_question import PublicPersonQuestion

from parladata.models.organization import CLASSIFICATIONS as ORGANIZATION_CLASSIFICATIONS
from parlacards.models import (
    SessionTfidf,
    VotingDistance,
    PersonMonthlyVoteAttendance,
    GroupMonthlyVoteAttendance,
    PersonTfidf,
    GroupTfidf,
    GroupVotingDistance,
    DeviationFromGroup,
    SessionGroupAttendance,
    OrganizationVoteDiscord,
)

from parlacards.serializers.media import MediaReportSerializer
from parlacards.serializers.person import PersonBasicInfoSerializer
from parlacards.serializers.organization import OrganizationBasicInfoSerializer, RootOrganizationBasicInfoSerializer
from parlacards.serializers.legislation import LegislationSerializer, LegislationDetailSerializer
from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.voting_distance import VotingDistanceSerializer, GroupVotingDistanceSerializer
from parlacards.serializers.membership import MembershipSerializer
from parlacards.serializers.style_scores import StyleScoresSerializer
from parlacards.serializers.speech import (
    SpeechSerializer,
    HighlightSerializer,
    SpeechWithSessionSerializer,
    ShortenedSpeechWithSessionSerializer,
)
from parlacards.serializers.quote import QuoteWithSessionSerializer
from parlacards.serializers.vote import (
    VoteSerializer,
    SessionVoteSerializer,
    ToolsDiscordSerializer,
)
from parlacards.serializers.tfidf import TfidfSerializer
from parlacards.serializers.facets import GroupFacetSerializer, PersonFacetSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.agenda_item import AgendaItemsSerializer, MinutesAgendaItemSerializer, MinutesAgendaItemWithSessionSerializer, MinutesAgendaItemWithSessionWithoutVotesSerializer
from parlacards.serializers.common import (
    CardSerializer,
    PersonScoreCardSerializer,
    GroupScoreCardSerializer,
    ScoreSerializerField,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    MonthlyAttendanceSerializer,
    SessionScoreCardSerializer,
    MandateSerializer
)
from parlacards.serializers.public_question import PublicPersonQuestionSerializer

from parlacards.solr import parse_search_query_params, solr_select
from parlacards.pagination import calculate_cache_key_for_page, create_paginator, create_solr_paginator
from parlacards.recaptcha import recaptcha_data
from parladata.exceptions import NoMembershipException
from rest_framework.exceptions import NotFound

#
# PERSON
#
class PersonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        person_serializer = PersonBasicInfoSerializer(
            person,
            context=self.context
        )
        return person_serializer.data


class PersonVocabularySizeCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonVocabularySize')


class PersonAvgSpeechesPerSessionCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonAvgSpeechesPerSession')


class PersonVoteAttendanceCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonVoteAttendance')


class PersonMonthlyVoteAttendanceCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        from_timestamp = self.from_timestamp.replace(day=1)
        monthly_attendance = PersonMonthlyVoteAttendance.objects.filter(
            person=person,
            playing_field=self.playing_field,
            timestamp__range=(from_timestamp, self.to_timestamp),
        ).order_by('timestamp')
        return MonthlyAttendanceSerializer(monthly_attendance, many=True).data


class PersonNumberOfQuestionsCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonNumberOfQuestions')


class GroupVocabularySizeCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupVocabularySize')


class PersonBallotCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        ballots = Ballot.objects.filter(
            personvoter=person,
            vote__timestamp__range=(self.from_timestamp, self.to_timestamp)
        ).order_by(
            '-vote__timestamp',
            '-id' # fallback ordering
        )

        option_counts = ballots.values('option').order_by('option').annotate(count=Count('option'))
        all_options = {o['option']: o['count'] for o in option_counts}

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            ballots = ballots.filter(vote__motion__text__icontains=text)

        # get options filter
        if text := self.context.get('GET', {}).get('options', None):
            options = text.split(',')
            ballots = ballots.filter(option__in=options)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), ballots, prefix='ballots:')

        # serialize ballots
        ballot_serializer = BallotSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                'ballots': ballot_serializer.data,
                'all_options': all_options,
            },
        }


class PersonMembershipCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # do not show memberships in root organization or parties
        filtered_classifications = [
            classification[0] for classification
            in filter(lambda x: x[0] != 'pg' and x[0] != 'root', ORGANIZATION_CLASSIFICATIONS)
        ]

        memberships = PersonMembership.valid_at(self.context['request_date']).filter(
            member=person,
            organization__classification__in=filtered_classifications
        ).exclude(
            role='voter'
        )
        membership_serializer = MembershipSerializer(memberships, context=self.context, many=True)
        return membership_serializer.data


class MostVotesInCommonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        voters = self.playing_field.query_voters(self.context['card_date'])
        most_in_common = VotingDistance.objects.filter(
            person=person,
            target__in=voters,
            timestamp__range=(self.from_timestamp, self.to_timestamp)
        ).exclude(
            target=person
        ).order_by(
            'target',
            '-timestamp',
            'value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(most_in_common)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=True)

        distances_serializer = VotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data

    results = serializers.SerializerMethodField()


class LeastVotesInCommonCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        voters = self.playing_field.query_voters(self.context['card_date'])

        least_in_common = VotingDistance.objects.filter(
            person=person,
            target__in=voters,
            timestamp__range=(self.from_timestamp, self.to_timestamp)
        ).exclude(
            target=person
        ).order_by(
            'target',
            '-timestamp',
            'value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(least_in_common)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=False)

        distances_serializer = VotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data

    results = serializers.SerializerMethodField()


class DeviationFromGroupCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='DeviationFromGroup')


class GroupDeviationFromGroupCardSerializer(GroupScoreCardSerializer):
    def get_results(self, group):
        # TODO this is very similar to
        # ScoreSerializerField - consider refactoring

        people = group.query_members(self.context['card_date'])

        relevant_deviation_querysets = [
            DeviationFromGroup.objects.filter(
                timestamp__range=(self.from_timestamp, self.to_timestamp),
                person=person
            ).order_by(
                '-timestamp'
            )[:1] for person in people
        ]
        relevant_deviation_ids = DeviationFromGroup.objects.none().union(
            *relevant_deviation_querysets
        ).values(
            'id'
        )
        relevant_deviations = DeviationFromGroup.objects.filter(
            id__in=relevant_deviation_ids
        )

        return [
            {
                'person': CommonPersonSerializer(
                    deviation_score.person,
                    context=self.context
                ).data,
                'value': deviation_score.value
            } for deviation_score in relevant_deviations
        ]


class StyleScoresCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        serializer = StyleScoresSerializer(person, context=self.context)
        return serializer.data

class GroupStyleScoresCardSerializer(GroupScoreCardSerializer):
    def get_results(self, person):
        serializer = StyleScoresSerializer(person, context=self.context)
        return serializer.data

class NumberOfSpokenWordsCardSerializer(PersonScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='PersonNumberOfSpokenWords')


class PersonTfidfCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        latest_score = PersonTfidf.objects.filter(
            person=person,
            timestamp__range=(self.from_timestamp, self.to_timestamp),
        ).order_by(
            '-timestamp'
        ).first()

        if latest_score:
            tfidf_scores = PersonTfidf.objects.filter(
                person=person,
                timestamp=latest_score.timestamp,
            )
        else:
            tfidf_scores = []

        serializer = TfidfSerializer(
            tfidf_scores,
            many=True,
            context=self.context
        )

        return serializer.data


class PersonSpeechesCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        solr_params = parse_search_query_params(
            self.context.get('GET', {}),
            people_ids=[person.id],
            group_ids=None,
            highlight=True,
            mandate=self.mandate.id
        )
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # TODO this might be better done by Solr directly
        # sort before serializing
        # first by order, then by date (in reverse order of sort preference)
        paged_object_list.sort(key=lambda speech: speech.order, reverse=True)
        paged_object_list.sort(key=lambda speech: speech.start_time, reverse=True)

        # serialize speeches
        speeches_serializer = ShortenedSpeechWithSessionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class PublicPersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        public_person_questions = PublicPersonQuestion.objects.filter(
            recipient_person=person,
            created_at__range=(self.from_timestamp, self.to_timestamp),
            approved_at__isnull=False
        ).exclude(
            rejected_at__isnull=False
        ).order_by(
            '-created_at',
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), public_person_questions)

        # serialize questions
        person_public_questions_serializer = PublicPersonQuestionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            **recaptcha_data,
            'results': person_public_questions_serializer.data,
        }


class GroupSpeechesCardSerializer(GroupScoreCardSerializer):
    def get_results(self, group):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, group):
        parent_data = super().to_representation(group)

        solr_params = parse_search_query_params(
            self.context.get('GET', {}),
            group_ids=[group.id],
            highlight=True,
            mandate=self.mandate.id
        )
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # serialize speeches
        speeches_serializer = ShortenedSpeechWithSessionSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


#
# MISC
#
class LegislationDetailCardSerializer(CardSerializer):
    def get_results(self, obj):
        # obj is the law
        serializer = LegislationDetailSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, obj):
        serializer = MandateSerializer(
            obj.mandate,
            context=self.context
        )
        return serializer.data


#
# ORGANIZATION
#
class GroupCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        serializer = OrganizationBasicInfoSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        members = instance.query_members_by_role(
            role='member',
            timestamp=self.context['card_date']
        ).order_by(
            'latest_name',
            'id' # fallback ordering
        )

        if not members.exists():
            # this "if" is an optimization
            # if there are no members we should
            # not have to cache.
            #
            # it also works around a bug introduced in
            # parlacards.pagination.calculate_cache_key_for_page
            # if paged_object_list is empty call to max() fails
            #
            # we still need to return a properly structured object
            paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), Question.objects.none())
            return {
                **parent_data,
                **pagination_metadata,
                'results': {
                    **parent_data['results'],
                    'members': [],
                }
            }

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), members, prefix='members:')
        page_cache_key = f'GroupCardSerializer_{calculate_cache_key_for_page(paged_object_list, pagination_metadata)}'

        # if there's something in the cache return it, otherwise serialize and save
        if cached_members := cache.get(page_cache_key):
            page_data = cached_members
        else:
            people_serializer = CommonPersonSerializer(
                paged_object_list,
                many=True,
                context=self.context
            )
            page_data = people_serializer.data
            cache.set(page_cache_key, page_data)

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                **parent_data['results'],
                'members': page_data,
            },
        }


class GroupMembersCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the group
        members = instance.query_members(
            timestamp=self.context['card_date']
        ).order_by(
            'latest_name',
            'id' # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), members)

        people_serializer = CommonPersonSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': people_serializer.data,
        }


class GroupMonthlyVoteAttendanceCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        from_timestamp = self.from_timestamp.replace(day=1)
        monthly_attendance = GroupMonthlyVoteAttendance.objects.filter(
            group=obj,
            playing_field=self.playing_field,
            timestamp__range=(from_timestamp, self.to_timestamp)
        ).order_by('timestamp')
        return MonthlyAttendanceSerializer(monthly_attendance, many=True).data


class GroupNumberOfQuestionsCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupNumberOfQuestions')


class GroupVoteAttendanceCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupVoteAttendance')


class GroupMostVotesInCommonCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is the group
        voters = self.playing_field.query_voters(self.context['card_date'])
        most_in_common = GroupVotingDistance.objects.filter(
            group=obj,
            target__in=voters,
            timestamp__range=(self.from_timestamp, self.to_timestamp)
        ).order_by(
            'target',
            '-timestamp',
            'value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(most_in_common)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=True)

        distances_serializer = GroupVotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data


class GroupLeastVotesInCommonCardSerializer(GroupScoreCardSerializer):
    def get_results(self, group):
        # obj is the group
        voters = self.playing_field.query_voters(self.context['request_date'])
        least_in_common = GroupVotingDistance.objects.filter(
            group=group,
            target__in=voters,
            timestamp__range=(self.from_timestamp, self.to_timestamp)
        ).order_by(
            'target',
            '-timestamp',
            '-value',
        ).distinct(
            'target'
        )

        # sorting in place is slightly more efficient
        sorted_distances = list(least_in_common)
        sorted_distances.sort(key=lambda distance: distance.value, reverse=False)

        distances_serializer = GroupVotingDistanceSerializer(
            sorted_distances[:5],
            many=True,
            context=self.context
        )

        return distances_serializer.data


class GroupDiscordCardSerializer(GroupScoreCardSerializer):
    results = ScoreSerializerField(property_model_name='GroupDiscord')


class RootGroupBasicInfoCardSerializer(CardSerializer):
    def get_results(self, mandate):
        try:
            root_organization, playing_field = mandate.query_root_organizations(self.context['request_date'])
        except NoMembershipException as e:
            raise NotFound(detail=str(e), code=404)

        serializer = RootOrganizationBasicInfoSerializer(
            root_organization,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data


#
# SESSION
#
class SessionAgendaItemCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # obj is the session
        serializer = AgendaItemsSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class SessionMinutesCardSerializer(SessionScoreCardSerializer):
    def get_results(self, session):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, session):
        parent_data = super().to_representation(session)

        agenda_items = AgendaItem.objects.filter(
            Q(datetime__lte=self.context['request_date']) | Q(datetime__isnull=True),
            session=session,
        ).order_by('order')

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), agenda_items)

        minutes_serializer = MinutesAgendaItemSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': minutes_serializer.data,
        }


class SingleMinutesCardSerializer(CardSerializer):
    def get_results(self, agenda_item):
        serializer = MinutesAgendaItemWithSessionSerializer(
            agenda_item,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, agenda_item):
        serializer = MandateSerializer(
            agenda_item.session.mandate,
            context=self.context
        )
        return serializer.data


class SessionSpeechesCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the session
        speeches = Speech.objects.filter_valid_speeches(self.context['request_date']).filter(
            session=instance
        ).order_by(
            'order',
            'id' # fallback ordering
        )

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), speeches)

        # serialize speeches
        speeches_serializer = SpeechSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class SpeechCardSerializer(CardSerializer):
    def get_results(self, speech):
        serializer = SpeechWithSessionSerializer(
            speech,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, speech):
        serializer = MandateSerializer(
            speech.session.mandate,
            context=self.context
        )
        return serializer.data


class QuoteCardSerializer(CardSerializer):
    def get_results(self, quote):
        serializer = QuoteWithSessionSerializer(
            quote,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, quote):
        serializer = MandateSerializer(
            quote.speech.session.mandate,
            context=self.context
        )
        return serializer.data


class VoteCardSerializer(CardSerializer):
    def get_results(self, vote):
        serializer = VoteSerializer(
            vote,
            context=self.context
        )
        return serializer.data

    def get_mandate(self, vote):
        serializer = MandateSerializer(
            vote.motion.session.mandate,
            context=self.context
        )
        return serializer.data


class GroupTfidfCardSerializer(GroupScoreCardSerializer):
    def get_results(self, obj):
        # obj is group
        mandate = Mandate.get_active_mandate_at(self.context['request_date'])
        from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(self.context['request_date'])
        latest_score = GroupTfidf.objects.filter(
            group=obj,
            timestamp__range=(from_timestamp, to_timestamp),
        ).order_by(
            '-timestamp'
        ).first()

        if latest_score:
            tfidf_scores = GroupTfidf.objects.filter(
                group=obj,
                timestamp=latest_score.timestamp,
            )
        else:
            tfidf_scores = []

        serializer = TfidfSerializer(
            tfidf_scores,
            many=True,
            context=self.context
        )

        return serializer.data


class SessionVotesCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # this is implemented in to_representation for pagination
        return None

    def to_representation(self, instance):
        parent_data = super().to_representation(instance)

        # instance is the session
        votes = Vote.objects.filter(
            motion__session=instance
        ).order_by(
            'timestamp',
            'id' # fallback ordering
        )

        # TODO: maybe lemmatize?, maybe search by each word separately?
        if text := self.context.get('GET', {}).get('text', None):
            votes = votes.filter(motion__text__icontains=text)

        passed_string = self.context.get('GET', {}).get('passed', None)
        if passed_string in ['true', 'false']:
            passed_bool = passed_string == 'true'
            votes = votes.filter(result=passed_bool)

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), votes)

        # serialize votes
        vote_serializer = SessionVoteSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': vote_serializer.data,
        }


#
# SPEECHES
#
class MandateSpeechCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id, highlight=True)
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params)

        # serialize speeches
        speeches_serializer = HighlightSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class MandateUsageByGroupCardSerializer(CardSerializer):
    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data

    def get_results(self, mandate):
        solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id, facet=True)
        solr_response = solr_select(**solr_params, per_page=0)

        if not solr_response.get('facet_counts', {}).get('facet_fields', {}).get('party_id', []):
            return None

        facet_counts = solr_response['facet_counts']['facet_fields']['party_id']
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {'group': Organization.objects.filter(pk=group_id).first(), 'value': value}
            for (group_id, value) in facet_counts_tuples
        ]

        facet_serializer = GroupFacetSerializer(
            objects,
            many=True,
            context=self.context
        )

        return facet_serializer.data


class MandateMostUsedByPeopleCardSerializer(CardSerializer):
    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data
    def get_results(self, mandate):
        people_ids = mandate.personmemberships.filter(role='voter').values_list('member_id', flat=True)
        solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id, facet=True)
        solr_response = solr_select(**solr_params, per_page=0)

        if not solr_response.get('facet_counts', {}).get('facet_fields', {}).get('person_id', []):
            return None

        # TODO make this better
        # slice first 10 items from the list to only show top 5 people
        # 5 times (id, value) = 10
        end_slice = 0
        people_count = 0
        for person_id in solr_response['facet_counts']['facet_fields']['person_id'][::2]:
            end_slice += 2
            if int(person_id) in people_ids:
                people_count += 1
            if people_count == 5:
                break

        facet_counts = solr_response['facet_counts']['facet_fields']['person_id'][:end_slice]
        facet_counts_tuples = zip(facet_counts[::2], facet_counts[1::2])
        objects = [
            {'person': Person.objects.filter(pk=person_id).first(), 'value': value}
            for (person_id, value) in facet_counts_tuples if int(person_id) in people_ids
        ]

        facet_serializer = PersonFacetSerializer(
            objects,
            many=True,
            context=self.context
        )

        return facet_serializer.data


class MandateLegislationCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None
    
    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        if self.context.get('GET', {}).get('text', None):
            solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id)
            paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params, document_type='law')
        else:
            legislation = Law.objects.filter(
                Q(timestamp__lte=self.context['request_date']) | Q(timestamp__isnull=True),
                session__mandate=mandate,
            )
            paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), legislation)

        # serialize legislation
        legislation_serializer = LegislationSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': legislation_serializer.data,
        }


class SearchDropdownSerializer(CardSerializer):
    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data

    def get_results(self, mandate):
        try:
            root_organization, playing_field = mandate.query_root_organizations(self.context['request_date'])
        except NoMembershipException as e:
            raise NotFound(detail=str(e), code=404)

        people_data = []
        groups_data = []

        text = self.context.get('GET', {}).get('text', None)

        if text and len(text) >= 2:
            leader = root_organization.query_members_by_role('leader', self.context['request_date']).order_by('personname__value', 'id')
            voters = playing_field.query_voters(self.context['request_date']).order_by('personname__value', 'id')

            # TODO: will this work correctly when people have multiple names?
            leader = leader.filter(latest_name__icontains=text)
            voters = voters.filter(latest_name__icontains=text)

            people = leader.union(voters)

            person_serializer = CommonPersonSerializer(
                people[:10],
                many=True,
                context=self.context
            )
            people_data = person_serializer.data

            groups = playing_field.query_parliamentary_groups(self.context['request_date'])
            # TODO: will this work correctly when groups have multiple names?
            groups = groups.filter(
                Q(organizationname__value__icontains=text) | Q(organizationacronym__value__icontains=text)
            ).order_by('organizationname__value', 'id')
            group_serializer = CommonOrganizationSerializer(
                groups[:10],
                many=True,
                context=self.context
            )
            groups_data = group_serializer.data

        return {
            'people': people_data,
            'groups': groups_data,
        }


#
# MINUTES
#
class MandateMinutesCardSerializer(CardSerializer):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, mandate):
        serializer = MandateSerializer(
            mandate,
            context=self.context
        )
        return serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        solr_params = parse_search_query_params(self.context.get('GET', {}), mandate=mandate.id, highlight=True)
        paged_object_list, pagination_metadata = create_solr_paginator(self.context.get('GET', {}), solr_params, document_type='agenda_item')

        # serialize agenda items
        speeches_serializer = MinutesAgendaItemWithSessionWithoutVotesSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': speeches_serializer.data,
        }


class PersonMediaReportsCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        reports = MediaReport.objects.filter(
            medium__active=True,
            mentioned_people=person.id
        ).order_by(
            'report_date'
        )[:50]
        # TODO do this better
        # this tries to reduce loading time and shorten the card
        # by only showing the latest 50 reports

        serializer = MediaReportSerializer(
            reports,
            many=True,
            context=self.context
        )
        return serializer.data


class GroupMediaReportsCardSerializer(GroupScoreCardSerializer):
    def get_results(self, organization):
        reports = MediaReport.objects.filter(
            medium__active=True,
            mentioned_organizations=organization.id
        ).order_by(
            'report_date'
        )[:50]
        # TODO do this better
        # this tries to reduce loading time and shorten the card
        # by only showing the latest 50 reports

        serializer = MediaReportSerializer(
            reports,
            many=True,
            context=self.context
        )
        return serializer.data

#
# TOOLS
#


class ToolsDiscordCardSerializer(CardSerializer):

    def get_results(self, organization):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, organization):
        mandate = Mandate.get_active_mandate_at(self.context["request_date"])
        serializer = MandateSerializer(mandate, context=self.context)
        return serializer.data

    def to_representation(self, organization):
        mandate = Mandate.get_active_mandate_at(self.context["request_date"])
        parent_data = super().to_representation(mandate) 

        root_organization, playing_field = mandate.query_root_organizations()

        self.context["organization"] = organization

        order_by = self.context.get("GET", {}).get("order_by", "date")
        if order_by == "date":
            order_by = "-vote__timestamp"
        else:
            order_by = "value"

        discords = OrganizationVoteDiscord.objects.filter(
            organization=organization, playing_field=playing_field
        ).prefetch_related("vote").order_by(order_by)

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), discords
        )

        discord_serializer = ToolsDiscordSerializer(
            paged_object_list,
            many=True,
            context=self.context,
        )

        playing_field_serializer = CommonOrganizationSerializer(
            playing_field, context=self.context
        )

        organizations = playing_field.query_parliamentary_groups()
        organizations_serializer = CommonOrganizationSerializer(
            organizations, context=self.context, many=True
        )

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                "votes": discord_serializer.data,
                "organizations": organizations_serializer.data
                + [playing_field_serializer.data],
            },
        }
