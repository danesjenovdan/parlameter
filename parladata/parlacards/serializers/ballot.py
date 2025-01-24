from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer
from parlacards.serializers.vote import BareVoteSerializer

# TODO
# class BallotSerializer(CommonCachableSerializer):
#     def calculate_cache_key(self, instance):
#         # instance is the vote
#         # TODO what if ballots change?
#         vote_timestamp = instance.vote.updated_at
#         person_timestamp = instance.personvoter.updated_at
#         ballot_timestamp = instance.updated_at
#         session_timestamp = instance.vote.motion.session.updated_at
#         timestamp = max([vote_timestamp, person_timestamp, ballot_timestamp, session_timestamp])
#         return f'BallotSerializer_{instance.id}_{instance.personvoter.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'


class BallotSerializer(CommonSerializer):
    def get_vote(self, obj):
        vote_serializer = BareVoteSerializer(obj.vote, context=self.context)
        return vote_serializer.data

    vote = serializers.SerializerMethodField()
    option = serializers.CharField()
