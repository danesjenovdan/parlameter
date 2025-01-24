from export.resources.group import (
    GroupDeviationFromGroupResource,
    GroupDiscordResource,
    GroupInfoResource,
    GroupMembersResource,
    GroupMonthlyVoteAttendanceResource,
    GroupNumberOfQuestionsResource,
    GroupStyleScoresResource,
    GroupTfidfResource,
    GroupVocabularySizeResource,
    GroupVoteAttendanceResource,
    GroupVotesInCommonResource,
)
from export.views.common import ExportResourceView


class ExportGroupDiscord(ExportResourceView):
    """
    Export group's discord from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_discord"
    resource = GroupDiscordResource()


class ExportGroupVocabularySize(ExportResourceView):
    """
    Export group's vocabulary size from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_vocabulary_size"
    resource = GroupVocabularySizeResource()


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


class ExportGroupDeviationFromGroup(ExportResourceView):
    """
    Export group's deviation from group from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_deviation_from_group"
    resource = GroupDeviationFromGroupResource()


class ExportGroupInfo(ExportResourceView):
    """
    Export group's basic information from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "group_basic_information"
    resource = GroupInfoResource()
