from django.contrib import admin
from import_export.admin import ExportMixin

from export.resources.group import GroupDiscordResource
from parlacards.admin.common import LatestScoresAdmin
from parlacards.models import GroupDiscord, OrganizationVoteDiscord


class GroupDiscordAdmin(ExportMixin, LatestScoresAdmin):
    resource_class = GroupDiscordResource


class OrganizationVoteDiscordAdmin(LatestScoresAdmin):
    pass
    # resource_class = GroupDiscordResource


admin.site.register(GroupDiscord, GroupDiscordAdmin)
admin.site.register(OrganizationVoteDiscord, OrganizationVoteDiscordAdmin)
