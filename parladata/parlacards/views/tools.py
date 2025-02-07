from parladata.models.organization import Organization

from parlacards.views.views import CardView

from parlacards.serializers.cards.tools.word_groups import WordGroupsCardSerializer

class WordGroupsCardView(CardView):
    '''Word groups view.'''
    thing = Organization
    card_serializer = WordGroupsCardSerializer
