from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.serializers.session import SessionSerializer


class SingleSessionCardSerializer(CardSerializer):
    def get_results(self, session):
        serializer = SessionSerializer(session, context=self.context)
        return serializer.data

    def get_mandate(self, session):
        serializer = MandateSerializer(session.mandate, context=self.context)
        return serializer.data
