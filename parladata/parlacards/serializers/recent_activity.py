from parlacards.serializers.ballot import BallotSerializer
from parlacards.serializers.common import CommonSerializer
from parlacards.serializers.question import QuestionSerializer
from parlacards.serializers.speech import RecentActivitySpeechSerializer
from parladata.models.ballot import Ballot
from parladata.models.question import Question
from parladata.models.speech import Speech


class EventSerializer(CommonSerializer):
    def to_representation(self, obj):
        # figure out which event type we're dealing with
        if isinstance(obj, Speech):
            serializer = RecentActivitySpeechSerializer(obj, context=self.context)
            return {"type": "speech", **serializer.data}

        if isinstance(obj, Ballot):
            serializer = BallotSerializer(obj, context=self.context)
            return {"type": "ballot", **serializer.data}

        if isinstance(obj, Question):
            serializer = QuestionSerializer(obj, context=self.context)
            return serializer.data  # type is included in QuestionSerializer

        raise ValueError(f"Cannot serialize {obj} as activity.")
