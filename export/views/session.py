from export.resources.session import (
    SessionSpeechesResource,
    SingleVoteResource,
    VoteResource,
)
from export.views.common import ExportResourceView


class ExportVotesView(ExportResourceView):
    """
    Export votes from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "votes"
    resource = VoteResource()


class ExportSessionSpeeches(ExportResourceView):
    """
    Export session speeches from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "session-speeches"
    resource = SessionSpeechesResource()


class ExportSingleVote(ExportResourceView):
    """
    Export a single vote from database and return it as a file in one of the allowed formats (json, csv).
    """

    filename = "single-vote"
    resource = SingleVoteResource()
