from collections import Counter

from django.core.cache import cache
from django.db.models import Count

from rest_framework import serializers

from parladata.models.ballot import Ballot

from parlacards.models import OrganizationVoteDiscord

from parlacards.serializers.session import SessionSerializer
from parlacards.serializers.link import LinkSerializer

from parlacards.serializers.common import (
    CommonSerializer,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
    CommonCachableSerializer
)

class VoteBallotSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, ballot):
        # if there is a personvoter, the cache key should take that into consideration
        if ballot.personvoter:
            ballot_timestamp = ballot.updated_at
            person_timestamp = ballot.personvoter.updated_at
            timestamp = max([ballot_timestamp, person_timestamp])
            return f'VoteBallotSerializer_{ballot.id}_{ballot.personvoter.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

        return f'VoteBallotSerializer_{ballot.id}_{ballot.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    person = serializers.SerializerMethodField()
    option = serializers.CharField()
    def get_person(self, ballot):
        serializer = CommonPersonSerializer(
            ballot.personvoter,
            context=self.context,
        )
        return serializer.data


class VoteGroupSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, group):
        group_timestamp = group.updated_at
        vote = self.context['vote']
        vote_timestamp = vote.updated_at

        memberships_updated_at = list(vote.motion.session.organizations.first().personmemberships_children.filter(
            role='voter'
        ).active_at(vote.timestamp).values_list('updated_at', flat=True))

        timestamp = max([group_timestamp, vote_timestamp] + memberships_updated_at)
        return f'VoteGroupSerializer_{group.id}_{self.context["vote"].id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_group_ballots(self, group):
        vote_ballots = Ballot.objects.filter(vote=self.context['vote'])

        group_ballots = vote_ballots.filter(
            personvoter__in=group.query_members(self.context['request_date']),
        )

        return group_ballots

    def get_annotated_group_ballots(self, group):
        annotated_group_ballots = self.get_group_ballots(group).values(
            'option'
        ).annotate(
            option_count=Count('option')
        ).order_by('-option_count')

        return annotated_group_ballots

    def get_outliers(self, group):
        # TODO this is very similar to get_stats in parladata.models.vote.Vote
        sum_of_all_ballots = sum(self.get_annotated_group_ballots(group).values_list('option_count', flat=True))
        if sum_of_all_ballots == 0:
            return []

        max_option = self.get_annotated_group_ballots(group).first()['option']

        filtered_group_ballots = self.get_group_ballots(group).exclude(option__in=['absent', max_option])
        outliers = [
            ballot.personvoter for ballot in filtered_group_ballots
        ]

        serializer = CommonPersonSerializer(
            outliers,
            many=True,
            context=self.context,
        )
        return serializer.data

    def get_max(self, group):
        # TODO only call DB once
        # TODO this is very similar to get_stats in parladata.models.vote.Vote
        sum_of_all_ballots = sum(self.get_annotated_group_ballots(group).values_list('option_count', flat=True))
        if sum_of_all_ballots != 0:
            max_option_percentage = self.get_annotated_group_ballots(group).first()['option_count'] * 100 / sum(self.get_annotated_group_ballots(group).values_list('option_count', flat=True))
            max_option = self.get_annotated_group_ballots(group).first()['option']
        else:
            max_option = None
            max_option_percentage = None
        return {
            'max_option_percentage': max_option_percentage,
            'max_option': max_option
        }

    def get_votes(self, group):
        group_votes_params = {
            option_sum['option']: option_sum['option_count'] for
            option_sum in self.get_annotated_group_ballots(group)
        }
        return {
            key: group_votes_params.get(key, 0) for
            key in [option[0] for option in Ballot.OPTIONS]
        }

    def get_group(self, group):
        serializer = CommonOrganizationSerializer(
            group,
            context=self.context,
        )
        return serializer.data

    max = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()
    outliers = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()


class VoteSumsSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, vote):
        # instance is the vote
        # get the latest timestamp to calculate the cache key
        # it's either the vote or the latest update to the person
        vote_timestamp = vote.updated_at

        # there is a special case where the vote has no ballots
        # we handle it by checking the ballot count and assigning
        # latest_voter_timestamp to previously calculated vote_timestamp
        if vote.ballots.count() == 0:
            return f'VoteSumsSerializer_{vote.id}_{vote_timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

        # the other special case is when all the ballots are anonymous
        elif vote.ballots.filter(personvoter__isnull=False).count() == 0:
            latest_voter_timestamp = vote_timestamp

        # we have ballots and at least one of them has a personvoter
        else:
            latest_voter_timestamp = vote.ballots.filter(personvoter__isnull=False).order_by(
                '-personvoter__updated_at'
            ).values(
                'personvoter__updated_at'
            ).first()['personvoter__updated_at']

        # there are ballots so we need the latest ballot update
        latest_ballot_timestamp = vote.ballots.all().order_by(
            '-updated_at'
        ).values(
            'updated_at'
        ).first()['updated_at']

        # finally we calculate the timestamp and cache key
        timestamp = max([vote_timestamp, latest_voter_timestamp, latest_ballot_timestamp])
        return f'VoteSumsSerializer_{vote.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def to_representation(self, instance):
        # instance is vote
        cache_key = self.calculate_cache_key(instance)
        cached_representation = cache.get(cache_key)
        if cached_representation:
            return cached_representation

        representation = instance.get_option_counts()
        cache.set(cache_key, representation)
        return representation


class VoteGovernmentSideSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, vote):
        timestamp = vote.updated_at
        # TODO get latest membership timestamp
        return f'VoteGovernmentSideSerializer_{vote.id}_{self.context["gov_side"]}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_outliers(self, vote):
        # TODO implemet this
        return []

    def get_max(self, vote):
        return vote.get_stats(gov_side=self.context['gov_side'])

    def get_votes(self, vote):
        return vote.get_option_counts(gov_side=self.context['gov_side'])

    def get_group(self, vote):
        return {
            'name': self.context['gov_side'],
            'acronym': None,
            'slug': None
        }

    max = serializers.SerializerMethodField()
    votes = serializers.SerializerMethodField()
    outliers = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()


class VoteStatsSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is the vote
        return f'VoteStatsSerializer_{instance.id}_{instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    # for is a reserved word FML
    def to_representation(self, instance):
        # instance is vote
        cache_key = self.calculate_cache_key(instance)
        cached_representation = cache.get(cache_key)
        if cached_representation:
            return cached_representation

        representation = instance.get_stats()
        cache.set(cache_key, representation)
        return representation


class VoteSerializer(CommonSerializer):
    # Use this when context['date'] should be the date of the vote.
    #
    # This is needed when using the CommonPersonSerializer or similar to return
    # the state of the person on the day of the vote, or when we need all the
    # groups/people active on the day of the vote.
    #
    # We should make a copy of the context object since we don't want to mess
    # with other serializers (a shallow copy here is good enough).
    def _get_context_for_vote_date(self, vote):
        new_context = dict.copy(self.context)
        new_context['vote'] = vote
        new_context['date'] = vote.timestamp
        new_context['request_date'] = vote.timestamp
        return new_context

    def get_government_sides(self, vote):
        org = vote.motion.session.organizations.first()

        coalition_organization_membership = org.organizationmemberships_children.active_at(
                vote.timestamp
            ).filter(
                member__classification='coalition'
            ).first()

        if not coalition_organization_membership:
            return []

        coalition_context = dict.copy(self.context)
        coalition_context['gov_side'] = 'coalition'
        coaliton_serializer = VoteGovernmentSideSerializer(
            vote,
            context=coalition_context
        )
        opposition_context = dict.copy(self.context)
        opposition_context['gov_side'] = 'opposition'
        opposition_serializer = VoteGovernmentSideSerializer(
            vote,
            context=opposition_context
        )
        return [coaliton_serializer.data, opposition_serializer.data]

    def get_abstract_visible(self, vote):
        return False

    def get_session(self, vote):
        serializer = SessionSerializer(
            vote.motion.session,
            context=self.context,
        )
        return serializer.data

    def get_result(self, vote):
        serializer = VoteStatsSerializer(
            vote,
            context=self.context,
        )
        return serializer.data

    def get_members(self, vote):
        # TODO these are now all cached together
        # but initial load still takes three minutes in Ukraine

        # there is a special case where the vote has no ballots
        # we can return []
        if vote.ballots.count() == 0:
            return []

        # the other special case is when all the ballots are anonymous
        # we can return []
        if vote.ballots.filter(personvoter__isnull=False).count() == 0:
            return []

        # get the latest timestamp to calculate the cache key
        # it's either the vote or the latest update to the person
        vote_timestamp = vote.timestamp

        # we did not return so we have ballots and at least one of them has a personvoter
        latest_voter_timestamp = vote.ballots.filter(personvoter__isnull=False).order_by(
            '-personvoter__updated_at'
        ).values(
            'personvoter__updated_at'
        ).first()['personvoter__updated_at']

        memberships_updated_at = list(vote.motion.session.organizations.first().personmemberships_children.filter(
            role='voter'
        ).active_at(vote.timestamp).values_list('updated_at', flat=True))


        # latest ballot update
        latest_ballot_timestamp = vote.ballots.all().order_by(
            '-updated_at'
        ).values(
            'updated_at'
        ).first()['updated_at']

        timestamp = max([vote_timestamp, latest_voter_timestamp, latest_ballot_timestamp] + memberships_updated_at)
        cache_key = f'SingleVoteMembers__{vote.id}__{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

        # if there's something in the cache, return
        if cached_member_ballots := cache.get(cache_key):
            return cached_member_ballots

        # nothing in the cache, do the math and set the cache

        # we want to serialize people with the state on the day of the vote
        new_context = self._get_context_for_vote_date(vote)

        serializer = VoteBallotSerializer(
            vote.ballots.all(),
            many=True,
            context=new_context,
        )
        cache.set(cache_key, serializer.data)

        return serializer.data

    def get_groups(self, vote):
        # there is a horrible case where the vote has no ballots
        # we can return []
        if vote.ballots.count() == 0:
            return []

        # the other horrible case is when all the ballots are anonymous
        # we can return []
        if vote.ballots.filter(personvoter__isnull=False).count() == 0:
            return []

        # we want to get and serialize groups that were active on the day of the vote
        # this also includes new_context['vote'] that is needed by VoteGroupSerializer
        new_context = self._get_context_for_vote_date(vote)

        groups = vote.motion.session.organization.query_parliamentary_groups(new_context['date'])

        serializer = VoteGroupSerializer(
            groups,
            many=True,
            context=new_context,
        )
        return serializer.data

    def get_agenda_items(self, vote):
        return None

    def get_documents(self, vote):
        serializer = LinkSerializer(
            vote.motion.links.all().exclude(tags__name='vote-pdf').exclude(note='analyse').order_by('id'),
            many=True,
            context=self.context,
        )
        return serializer.data

    def get_external_analysis(self, vote):
        serializer = LinkSerializer(
            vote.motion.links.filter(note='analyse').order_by('id'),
            many=True,
            context=self.context,
        )
        return serializer.data

    def get_legislation(self, vote):
        return None

    def get_all_votes(self, vote):
        serializer = VoteSumsSerializer(
            vote,
            context=self.context,
        )
        return serializer.data

    all_votes = serializers.SerializerMethodField()
    government_sides = serializers.SerializerMethodField()
    abstract_visible = serializers.SerializerMethodField() # TODO this is faked
    session = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    agenda_items = serializers.SerializerMethodField() # TODO this is faked
    documents = serializers.SerializerMethodField()
    external_analysis = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')
    legislation = serializers.SerializerMethodField() # TODO this is faked


class SessionVoteSerializer(CommonSerializer):
    def get_passed(self, obj):
        # obj is the vote
        return obj.result

    def get_is_outlier(self, obj):
        # TODO some day
        return False

    def get_has_outliers(self, obj):
        # TODO before some day
        return False

    def get_has_named_votes(self, obj):
        # TODO before some day
        return True

    def get_title(self, obj):
        # TODO return motion object 
        # and handle it on the front-end
        # TODO changed obj.motion.title to obj.name   check this if has a sense
        return obj.name

    def get_all_votes(self, obj):
        # obj is the vote
        serializer = VoteSumsSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    all_votes = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    is_outlier = serializers.SerializerMethodField()
    has_outliers = serializers.SerializerMethodField()
    has_named_votes = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField()


class BareVoteSerializer(SessionVoteSerializer):
    def get_session(self, obj):
        # obj is the vote
        serializer = SessionSerializer(
            obj.motion.session,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()


class SpeechVoteSerializer(CommonSerializer):
    result = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    title = serializers.CharField(source='name')
    votes = serializers.SerializerMethodField()

    def get_result(self, obj):
        # obj is the vote
        serializer = VoteStatsSerializer(
            obj,
            context=self.context
        )
        return serializer.data

    def get_votes(self, obj):
        # obj is the vote
        serializer = VoteSumsSerializer(
            obj,
            context=self.context
        )
        return serializer.data


class ToolsDiscordSerializer(CommonSerializer):
    title = serializers.CharField(source='vote.name')
    session = serializers.SerializerMethodField()
    vote_id = serializers.IntegerField(source="vote.id")
    value = serializers.FloatField()
    passed = serializers.BooleanField(source="vote.result")
    timestamp = serializers.DateTimeField(source="vote.timestamp")

    def get_session(self, discord):
        serializer = SessionSerializer(
            discord.vote.motion.session,
            context=self.context
        )
        return serializer.data
