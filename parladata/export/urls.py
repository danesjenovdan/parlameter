from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from export.views.group import *
from export.views.misc import *
from export.views.person import *
from export.views.session import *

urlpatterns = [
    # MISC
    path("misc/members/", ExportParliamentMembersView.as_view()),
    path("misc/groups/", ExportParliamentGroupsView.as_view()),
    path("misc/sessions/", ExportSessionView.as_view()),
    path("misc/legislation/", ExportMiscLegislationView.as_view()),
    # next misc endpoints are not implemented because they are not useful
    # path('misc/last-session/', LastSession.as_view()),
    # path('misc/search/', SearchDropdown.as_view()),
    # path('misc/menu-search/', SearchDropdown.as_view()),
    # path('misc/basic-information/', RootOrganization.as_view()),
    # PEOPLE
    path("person/basic-information/", ExportPersonInfo.as_view()),
    path("person/votes/", ExportPersonBallots.as_view()),
    path("person/questions/", ExportPersonQuestions.as_view()),
    path("person/memberships/", ExportPersonMembership.as_view()),
    path("person/most-votes-in-common/", ExportVotingDistance.as_view()),
    path("person/least-votes-in-common/", ExportVotingDistance.as_view()),
    path("person/agreement-with-group/", ExportAgreementWithGroup.as_view()),
    path(
        "person/average-number-of-speeches-per-session/",
        ExportPersonAvgSpeechesPerSession.as_view(),
    ),
    path("person/number-of-questions/", ExportPersonNumberOfQuestions.as_view()),
    path("person/vote-attendance/", ExportPersonVoteAttendance.as_view()),
    # person/recent-activity it is not implemented because it is not useful
    # path('person/recent-activity/', RecentActivity.as_view()),
    path(
        "person/monthly-vote-attendance/", ExportPersonMonthlyVoteAttendance.as_view()
    ),
    path("person/style-scores/", ExportPersonStyleScores.as_view()),
    path("person/number-of-spoken-words/", ExportPersonNumberOfSpokenWords.as_view()),
    path("person/tfidf/", ExportPersonTfidfView.as_view()),
    # person/speeches it is not implemented because it is not useful
    # path('person/speeches/', PersonSpeechesView.as_view()),
    # person/media-reports it is not implemented because it is not useful
    # path('person/media-reports/', PersonMediaReportsView.as_view()),
    # # next two endpoints are duplicated because we need the same data on both cards
    path("person/public-questions/", ExportPersonPublicQuestionView.as_view()),
    path("person/public-answers/", ExportPersonPublicQuestionView.as_view()),
    # GROUPS
    path("group/unity/", ExportGroupUnity.as_view()),
    path("group/basic-information/", ExportGroupInfo.as_view()),
    path("group/members/", ExportGroupMembers.as_view()),
    path("group/number-of-questions/", ExportGroupNumberOfQuestions.as_view()),
    path("group/monthly-vote-attendance/", ExportGroupMonthlyVoteAttendance.as_view()),
    # group/questions it is not implemented because it is not useful
    # path('group/questions/', GroupQuestions.as_view()),
    path("group/vote-attendance/", ExportGroupVoteAttendance.as_view()),
    # group/votes it is not implemented because it is not useful
    # path('group/votes/', GroupBallots.as_view()),
    path("group/most-votes-in-common/", ExportGroupVotesInCommon.as_view()),
    path("group/least-votes-in-common/", ExportGroupVotesInCommon.as_view()),
    # group/agreement-with-group only shows people who are active today
    path("group/agreement-with-group/", ExportGroupAgreementWithGroup.as_view()),
    path("group/tfidf/", ExportGroupTfidf.as_view()),
    path("group/style-scores/", ExportGroupStyleScores.as_view()),
    # group/speeches it is not implemented because it is not useful
    # path('group/speeches/', GroupSpeechesView.as_view()),
    # group/media-reports it is not implemented because it is not useful
    # path('group/media-reports/', GroupMediaReportsView.as_view()),
    # SESSIONS
    path("session/votes/", ExportVotesView.as_view()),
    path("session/legislation/", ExportLegislationView.as_view()),
    # next endpoints it is not implemented because it is not useful and can be accessed through API
    path("session/speeches/", ExportSessionSpeeches.as_view()),
    # path('session/votes/', SessionVotes.as_view()),
    # path('session/single/', SingleSession.as_view()),
    # path('session/tfidf/', SessionTfidfView.as_view()),
    # path('session/agenda-items/', SessionAgendaItemsView.as_view()),
    # path('session/minutes/', SessionMinutesView.as_view()),
    path("vote/single/", ExportSingleVote.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "csv"])
