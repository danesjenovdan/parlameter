from export.resources.misc import (
    GroupsResource,
    LegislationResource,
    MPResource,
    SessionResource,
)
from export.views.common import ExportResourceView


class ExportParliamentMembersView(ExportResourceView):
    """
    Export all parliament members from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "parliament-members"
    resource = MPResource()


class ExportParliamentGroupsView(ExportResourceView):
    """
    Export all parliament members from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "parliament-members"
    resource = GroupsResource()


class ExportLegislationView(ExportResourceView):
    """
    Export all legislation from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "legislation"
    resource = LegislationResource()


class ExportSessionView(ExportResourceView):
    """
    Export all sessions from database and return them as a file in one of the allowed formats (json, csv).
    """

    filename = "sessions"
    resource = SessionResource()
