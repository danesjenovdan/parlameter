from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.common import Mandate
from parladata.models.session import Session
from parladata.models.speech import Speech
from parladata.models.vote import Vote
from parladata.models.legislation import Law
from parladata.models.agenda_item import AgendaItem

from parlacards.models import Quote

from parlacards.serializers.cards import (
    GroupMediaReportsCardSerializer,
    PersonCardSerializer,
    GroupMembersCardSerializer,
    PersonMediaReportsCardSerializer,
    SearchDropdownSerializer,
    SessionSpeechesCardSerializer,
    SessionTfidfCardSerializer,
    MiscMembersCardSerializer,
    MiscGroupsCardSerializer,
    GroupCardSerializer,
    LegislationCardSerializer,
    PersonVocabularySizeCardSerializer,
    GroupVocabularySizeCardSerializer,
    PersonBallotCardSerializer,
    PersonQuestionCardSerializer,
    MostVotesInCommonCardSerializer,
    LeastVotesInCommonCardSerializer,
    PersonMembershipCardSerializer,
    PersonAvgSpeechesPerSessionCardSerializer,
    DeviationFromGroupCardSerializer,
    GroupDeviationFromGroupCardSerializer,
    PersonNumberOfQuestionsCardSerializer,
    PersonVoteAttendanceCardSerializer,
    PersonMonthlyVoteAttendanceCardSerializer,
    GroupMonthlyVoteAttendanceCardSerializer,
    GroupNumberOfQuestionsCardSerializer,
    GroupQuestionCardSerializer,
    StyleScoresCardSerializer,
    GroupStyleScoresCardSerializer,
    NumberOfSpokenWordsCardSerializer,
    SessionLegislationCardSerializer,
    SpeechCardSerializer,
    VoteCardSerializer,
    PersonTfidfCardSerializer,
    GroupTfidfCardSerializer,
    GroupVoteAttendanceCardSerializer,
    GroupVoteCardSerializer,
    GroupMostVotesInCommonCardSerializer,
    GroupLeastVotesInCommonCardSerializer,
    PersonSpeechesCardSerializer,
    GroupSpeechesCardSerializer,
    GroupDiscordCardSerializer,
    SingleSessionCardSerializer,
    SessionVotesCardSerializer,
    MiscLastSessionCardSerializer,
    MandateSpeechCardSerializer,
    MandateUsageByGroupCardSerializer,
    MandateMostUsedByPeopleCardSerializer,
    MandateUsageThroughTimeInSpeechesCardSerializer,
    MandateUsageThroughTimeInAgendaItemsCardSerializer,
    MandateVotesCardSerializer,
    MandateLegislationCardSerializer,
    LegislationDetailCardSerializer,
    SessionAgendaItemCardSerializer,
    QuoteCardSerializer,
    RootGroupBasicInfoCardSerializer,
    SessionMinutesCardSerializer,
    SingleMinutesCardSerializer,
    MandateMinutesCardSerializer,
    PublicPersonQuestionCardSerializer,
    ToolsDiscordCardSerializer,
)
from parlacards.serializers.speech import SpeechSerializer
from parlacards.serializers.quote import QuoteSerializer
from parlacards.serializers.group_attendance import SessionGroupAttendanceSerializer
from parlacards.serializers.cards.person.recent_activity import RecentActivityCardSerializer
from parlacards.serializers.cards.misc.sessions import SessionsCardSerializer
from parlacards.serializers.public_question import PublicPersonQuestionSerializer

from django.core.cache import cache


class CardView(APIView):
    """
    A view meant to be extended.
    It checks if the thing exists and
    returns 404 if it can't find it.
    """
    thing = None
    card_serializer = None
    prefetch = None

    def get_serializer_data(self, request, the_thing):
        serializer = self.card_serializer(
            the_thing,
            context={
                'request_date': request.card_date,
                'card_date': request.card_date,
                'GET': request.GET
            }
        )
        return serializer.data

    def get(self, request, format=None):
        if not self.thing:
            raise NotImplementedError('You should define a thing to serialize.')

        if not self.card_serializer:
            raise NotImplementedError('You should define a serializer to use.')

        # if the thing with id exists return serialized data
        the_thing = self.thing.objects.filter(id=request.card_id)
        # prefetch if something was asked to be prefetched
        if self.prefetch:
            the_thing = the_thing.prefetch_related(*self.prefetch)
        if the_thing_to_serialize := the_thing.first():
            return Response(self.get_serializer_data(request, the_thing_to_serialize))

        # otherwise return 404
        return Response(status=status.HTTP_404_NOT_FOUND)


class CachedCardView(CardView):
    @staticmethod
    def calculate_cache_key(request):
        return f'{request.path}_{request.card_id}_{request.card_date.strftime("%Y-%m-%d")}'

    def get(self, request, format=None):
        cache_key = self.calculate_cache_key(request)

        # only try cache if not explicitly disabled
        if not request.GET.get('no_cache', False):
            if cached_content := cache.get(cache_key):
                return Response(cached_content)

        # if the thing with id exists return serialized data
        if the_thing := self.thing.objects.filter(id=request.card_id).first():
            serializer_data = self.get_serializer_data(request, the_thing)
            cache.set(cache_key, serializer_data)
            return Response(serializer_data)

        # otherwise return 404
        return Response(status=status.HTTP_404_NOT_FOUND)


class PersonInfo(CardView):
    """
    Show basic person info.
    """
    thing = Person
    card_serializer = PersonCardSerializer


class Voters(CardView):
    '''
    Show a list of all MPs belonging to an organization.
    '''
    thing = Organization
    card_serializer = MiscMembersCardSerializer


class GroupInfo(CardView):
    """
    Show basic info of organization.
    """
    thing = Organization
    card_serializer = GroupCardSerializer


class GroupMembers(CardView):
    """
    Show organization members.
    """
    thing = Organization
    card_serializer = GroupMembersCardSerializer


class ParliamentaryGroups(CardView):
    '''
    List parties in an organization.
    '''
    thing = Organization
    card_serializer = MiscGroupsCardSerializer


class GroupVoteAttendance(CardView):
    '''
    Group's attendance on votes.
    '''
    thing = Organization
    card_serializer = GroupVoteAttendanceCardSerializer


class Sessions(CardView):
    '''
    List sessions in a mandate.
    '''
    thing = Mandate
    card_serializer = SessionsCardSerializer


class Legislation(CardView):
    '''
    List legislation in a mandate.
    '''
    thing = Mandate
    card_serializer = LegislationCardSerializer


class VocabularySize(CardView):
    '''
    A person's vocabulary size.
    '''
    thing = Person
    card_serializer = PersonVocabularySizeCardSerializer


class GroupVocabularySize(CardView):
    '''
    An organization's vocabulary size.
    '''
    thing = Organization
    card_serializer = GroupVocabularySizeCardSerializer


class Ballots(CardView):
    '''
    A person's ballots.
    '''
    thing = Person
    card_serializer = PersonBallotCardSerializer


class GroupBallots(CardView):
    '''
    A person's ballots.
    '''
    thing = Organization
    card_serializer = GroupVoteCardSerializer


class Questions(CardView):
    '''
    A person's questions.
    '''
    thing = Person
    card_serializer = PersonQuestionCardSerializer


class MostVotesInCommon(CardView):
    '''
    A person's most equal voters.
    '''
    thing = Person
    card_serializer = MostVotesInCommonCardSerializer


class LeastVotesInCommon(CardView):
    '''
    A person's least equal voters.
    '''
    thing = Person
    card_serializer = LeastVotesInCommonCardSerializer


class PersonMembership(CardView):
    '''
    A person's memberships.
    '''
    thing = Person
    card_serializer = PersonMembershipCardSerializer


class PersonAvgSpeechesPerSession(CardView):
    '''
    A person's averaga number of speeches per session.
    '''
    thing = Person
    card_serializer = PersonAvgSpeechesPerSessionCardSerializer


class DeviationFromGroup(CardView):
    '''
    A person's deviation from group voting.
    '''
    thing = Person
    card_serializer = DeviationFromGroupCardSerializer


class GroupDeviationFromGroup(CardView):
    '''
    A person's deviation from group voting.
    '''
    thing = Organization
    card_serializer = GroupDeviationFromGroupCardSerializer


class PersonNumberOfQuestions(CardView):
    '''
    A person's number of questions.
    '''
    thing = Person
    card_serializer = PersonNumberOfQuestionsCardSerializer


class PersonVoteAttendance(CardView):
    '''
    A person's presence on votes.
    '''
    thing = Person
    card_serializer = PersonVoteAttendanceCardSerializer


class PersonMonthlyVoteAttendance(CardView):
    '''
    A person's monthly presence on votes.
    '''
    thing = Person
    card_serializer = PersonMonthlyVoteAttendanceCardSerializer


class RecentActivity(CardView):
    '''
    A person's recent activity.
    '''
    thing = Person
    card_serializer = RecentActivityCardSerializer


class PersonPublicQuestionView(CardView):
    thing = Person
    card_serializer = PublicPersonQuestionCardSerializer

    permission_classes = [AllowAny]

    def post(self, request):
        """
        This endpoint uses reCAPTCHA. Read about google recaptcha: https://developers.google.com/recaptcha/docs/v3
        Set recaptcha secret key in secrets.yaml for using recaptcha or keep it empty for test mode.
        """
        serializer = PublicPersonQuestionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GroupMonthlyVoteAttendance(CardView):
    '''
    A group's monthly presence on votes.
    '''
    thing = Organization
    card_serializer = GroupMonthlyVoteAttendanceCardSerializer


class GroupNumberOfQuestions(CardView):
    '''
    A group's number of questions.
    '''
    thing = Organization
    card_serializer = GroupNumberOfQuestionsCardSerializer


class GroupQuestions(CardView):
    '''
    A group's questions.
    '''
    thing = Organization
    card_serializer = GroupQuestionCardSerializer


class PersonStyleScores(CardView):
    '''
    A person's style scores.
    '''
    thing = Person
    card_serializer = StyleScoresCardSerializer


class GroupStyleScores(CardView):
    '''
    A person's style scores.
    '''
    thing = Organization
    card_serializer = GroupStyleScoresCardSerializer


class PersonNumberOfSpokenWords(CardView):
    '''
    A person's style scores.
    '''
    thing = Person
    card_serializer = NumberOfSpokenWordsCardSerializer


class SessionLegislation(CardView):
    thing = Session
    card_serializer = SessionLegislationCardSerializer


class SessionSpeeches(CardView):
    thing = Session
    card_serializer = SessionSpeechesCardSerializer


class SessionVotes(CardView):
    thing = Session
    card_serializer = SessionVotesCardSerializer


class SingleSpeech(CardView):
    thing = Speech
    card_serializer = SpeechCardSerializer


class SpeechQuote(CardView):
    thing = Quote
    card_serializer = QuoteCardSerializer

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = QuoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class SingleSession(CardView):
    thing = Session
    card_serializer = SingleSessionCardSerializer


class SingleVote(CardView):
    thing = Vote
    prefetch = ['ballots', 'ballots__personvoter'] # this saves ~300 queries on the Ukranian installation
    card_serializer = VoteCardSerializer


class SingleLegislation(CardView):
    thing = Law
    card_serializer = LegislationDetailCardSerializer


class SingleMinutes(CardView):
    thing = AgendaItem
    card_serializer = SingleMinutesCardSerializer


class PersonTfidfView(CardView):
    thing = Person
    card_serializer = PersonTfidfCardSerializer


class GroupTfidfView(CardView):
    thing = Organization
    card_serializer = GroupTfidfCardSerializer


class SessionTfidfView(CardView):
    thing = Session
    card_serializer = SessionTfidfCardSerializer


class SessionAgendaItemsView(CardView):
    thing = Session
    card_serializer = SessionAgendaItemCardSerializer


class SessionMinutesView(CardView):
    thing = Session
    card_serializer = SessionMinutesCardSerializer


class GroupMostVotesInCommon(CardView):
    '''
    A group's most equal voters.
    '''
    thing = Organization
    card_serializer = GroupMostVotesInCommonCardSerializer


class GroupLeastVotesInCommon(CardView):
    '''
    A group's least equal voters.
    '''
    thing = Organization
    card_serializer = GroupLeastVotesInCommonCardSerializer


class PersonSpeechesView(CardView):
    '''
    A person's speeches.
    '''
    thing = Person
    card_serializer = PersonSpeechesCardSerializer


class GroupSpeechesView(CardView):
    '''
    A person's speeches.
    '''
    thing = Organization
    card_serializer = GroupSpeechesCardSerializer


class GroupDiscordView(CardView):
    '''
    A group's discord score.
    '''
    thing = Organization
    card_serializer = GroupDiscordCardSerializer


class RootOrganization(CardView):
    '''
    Basic information of root organization.
    '''
    thing = Mandate
    card_serializer = RootGroupBasicInfoCardSerializer


class MandateVotes(CardView):
    '''
    Search votes for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateVotesCardSerializer


class MandateLegislation(CardView):
    '''
    Search laws for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateLegislationCardSerializer


class MandateMinutes(CardView):
    '''
    Search minutes for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateMinutesCardSerializer


class MandateSpeeches(CardView):
    '''
    Search speeches for a mandate.
    '''
    thing = Mandate
    card_serializer = MandateSpeechCardSerializer


class MandateUsageByGroup(CardView):
    '''
    Search speeches for a mandate and return word usage by group.
    '''
    thing = Mandate
    card_serializer = MandateUsageByGroupCardSerializer


class MandateMostUsedByPeople(CardView):
    '''
    Search speeches for a mandate and return word usage by group.
    '''
    thing = Mandate
    card_serializer = MandateMostUsedByPeopleCardSerializer


class MandateUsageThroughTimeInSpeeches(CardView):
    '''
    Search speeches for a mandate and return word usage through time.
    '''
    thing = Mandate
    card_serializer = MandateUsageThroughTimeInSpeechesCardSerializer


class MandateUsageThroughTimeInAgendaItems(CardView):
    '''
    Search agenda items for a mandate and return word usage through time.
    '''
    thing = Mandate
    card_serializer = MandateUsageThroughTimeInAgendaItemsCardSerializer


class LastSession(CardView):
    '''
    Latest session information.
    '''
    thing = Organization
    card_serializer = MiscLastSessionCardSerializer

    # TODO consider refactoring this
    # overriding because even if the parent organization
    # exists (which is the "thing" we supply the id of)
    # the session might not (new, empty installation) we
    # should return 404 if the session does not exist
    def get(self, request, format=None):
        # if the thing with id exists return serialized data
        if the_thing := self.thing.objects.filter(id=request.card_id).first():
            # the_thing is the parent organization,
            # we should check if any sessions exist
            if the_thing.sessions.filter(
                Q(motions__isnull=False) | Q(sessiontfidf_related__isnull=False)
            ).count() > 0:
                return Response(self.get_serializer_data(request, the_thing))

        # otherwise return 404
        return Response(status=status.HTTP_404_NOT_FOUND)


class SearchDropdown(CardView):
    '''
    Search field dropdown autocomplete data
    '''
    thing = Mandate
    card_serializer = SearchDropdownSerializer


class PersonMediaReportsView(CardView):
    '''
    A person's speeches.
    '''
    thing = Person
    card_serializer = PersonMediaReportsCardSerializer


class GroupMediaReportsView(CardView):
    '''
    A person's speeches.
    '''
    thing = Organization
    card_serializer = GroupMediaReportsCardSerializer


class ToolsDiscord(CardView):
    """
    Discord for organizations
    """

    thing = Organization
    card_serializer = ToolsDiscordCardSerializer
