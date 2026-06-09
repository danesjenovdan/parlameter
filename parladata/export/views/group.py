from export.resources.group import (
    GroupAgreementWithGroupResource,
    GroupInfoResource,
    GroupMembersResource,
    GroupMonthlyVoteAttendanceResource,
    GroupNumberOfQuestionsResource,
    GroupStyleScoresResource,
    GroupTfidfResource,
    GroupUnityResource,
    GroupVoteAttendanceResource,
    GroupVotesInCommonResource,
)
from export.views.common import ExportResourceView


class ExportGroupUnity(ExportResourceView):
    """
    Export group's unity from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_unity"
    resource = GroupUnityResource()


class ExportGroupNumberOfQuestions(ExportResourceView):
    """
    Export group's number of questions from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_number_of_questions"
    resource = GroupNumberOfQuestionsResource()


class ExportGroupMonthlyVoteAttendance(ExportResourceView):
    """
    Export group's monthly vote attendance from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_monthly_vote_attendance"
    resource = GroupMonthlyVoteAttendanceResource()


class ExportGroupVoteAttendance(ExportResourceView):
    """
    Export group's vote attendance from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_vote_attendance"
    resource = GroupVoteAttendanceResource()


class ExportGroupVotesInCommon(ExportResourceView):
    """
    Export group's votes in common from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_votes_in_common"
    resource = GroupVotesInCommonResource()


class ExportGroupTfidf(ExportResourceView):
    """
    Export group's tfidf from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_tfidf"
    resource = GroupTfidfResource()


class ExportGroupMembers(ExportResourceView):
    """
    Export group's members from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_members"
    resource = GroupMembersResource()


class ExportGroupStyleScores(ExportResourceView):
    """
    Export group's style scores from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_style_scores"
    resource = GroupStyleScoresResource()


class ExportGroupAgreementWithGroup(ExportResourceView):
    """
    Export group's agreement with group from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_agreement_with_group"
    resource = GroupAgreementWithGroupResource()


class ExportGroupInfo(ExportResourceView):
    """
    Export group's basic information from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_basic_information"
    resource = GroupInfoResource()
