from django.urls import path

from parlacards.views import *


urlpatterns = [
    path('misc/members/', Voters.as_view()),
    path('misc/groups/', ParliamentaryGroups.as_view()),
    path('misc/sessions/', Sessions.as_view()),
    path('misc/legislation/', Legislation.as_view()),
    path('misc/last-session/', LastSession.as_view()),
    path('misc/search/', SearchDropdown.as_view()),
    path('misc/menu-search/', SearchDropdown.as_view()),
    path('misc/basic-information/', RootOrganization.as_view()),

    path('person/basic-information/', PersonInfo.as_view()),
    path('person/vocabulary-size/', VocabularySize.as_view()),
    path('person/votes/', Ballots.as_view()),
    path('person/questions/', Questions.as_view()),
    path('person/memberships/', PersonMembership.as_view()),
    path('person/most-votes-in-common/', MostVotesInCommon.as_view()),
    path('person/least-votes-in-common/', LeastVotesInCommon.as_view()),
    path('person/deviation-from-group/', DeviationFromGroup.as_view()),
    path('person/average-number-of-speeches-per-session/', PersonAvgSpeechesPerSession.as_view()),
    path('person/number-of-questions/', PersonNumberOfQuestions.as_view()),
    path('person/vote-attendance/', PersonVoteAttendance.as_view()),
    path('person/recent-activity/', RecentActivity.as_view()),
    path('person/monthly-vote-attendance/', PersonMonthlyVoteAttendance.as_view()),
    path('person/style-scores/', PersonStyleScores.as_view()),
    path('person/number-of-spoken-words/', PersonNumberOfSpokenWords.as_view()),
    path('person/tfidf/', PersonTfidfView.as_view()),
    path('person/speeches/', PersonSpeechesView.as_view()),
    path('person/media-reports/', PersonMediaReportsView.as_view()),
    # next two endpoints are duplicated because we need the same data on both cards
    path('person/public-questions/', PersonPublicQuestionView.as_view()),
    path('person/public-answers/', PersonPublicQuestionView.as_view()),

    path('group/basic-information/', GroupInfo.as_view()),
    path('group/members/', GroupMembers.as_view()),
    path('group/vocabulary-size/', GroupVocabularySize.as_view()),
    path('group/number-of-questions/', GroupNumberOfQuestions.as_view()),
    path('group/monthly-vote-attendance/', GroupMonthlyVoteAttendance.as_view()),
    path('group/questions/', GroupQuestions.as_view()),
    path('group/vote-attendance/', GroupVoteAttendance.as_view()),
    path('group/votes/', GroupBallots.as_view()),
    path('group/most-votes-in-common/', GroupMostVotesInCommon.as_view()),
    path('group/least-votes-in-common/', GroupLeastVotesInCommon.as_view()),
    path('group/deviation-from-group/', GroupDeviationFromGroup.as_view()),
    path('group/tfidf/', GroupTfidfView.as_view()),
    path('group/style-scores/', GroupStyleScores.as_view()),
    path('group/speeches/', GroupSpeechesView.as_view()),
    path('group/discord/', GroupDiscordView.as_view()),
    path('group/media-reports/', GroupMediaReportsView.as_view()),

    path('session/legislation/', SessionLegislation.as_view()),
    path('session/speeches/', SessionSpeeches.as_view()),
    path('session/votes/', SessionVotes.as_view()),
    path('session/single/', SingleSession.as_view()),
    path('session/tfidf/', SessionTfidfView.as_view()),
    path('session/agenda-items/', SessionAgendaItemsView.as_view()),
    path('session/minutes/', SessionMinutesView.as_view()),

    path('speech/single/', SingleSpeech.as_view()),
    path('speech/quote/', SpeechQuote.as_view()),

    path('vote/single/', SingleVote.as_view()),
    path('legislation/single/', SingleLegislation.as_view()),
    path('minutes/single/', SingleMinutes.as_view()),

    path('search/votes/', MandateVotes.as_view()),
    path('search/minutes/', MandateMinutes.as_view()),
    path('search/legislation/', MandateLegislation.as_view()),
    path('search/speeches/', MandateSpeeches.as_view()),
    path('search/usage-by-group/', MandateUsageByGroup.as_view()),
    path('search/most-used-by-people/', MandateMostUsedByPeople.as_view()),
    path('search/usage-through-time-in-speeches/', MandateUsageThroughTimeInSpeeches.as_view()),
    path('search/usage-through-time-in-agenda-items/', MandateUsageThroughTimeInAgendaItems.as_view()),

    path("tools/discord/", ToolsDiscord.as_view()),
]

