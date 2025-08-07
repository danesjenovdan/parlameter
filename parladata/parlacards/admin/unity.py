from django.contrib import admin
from import_export.admin import ExportMixin

from export.resources.group import GroupUnityResource
from parlacards.admin.common import LatestScoresAdmin
from parlacards.models import GroupUnity


class GroupUnityAdmin(ExportMixin, LatestScoresAdmin):
    resource_class = GroupUnityResource


admin.site.register(GroupUnity, GroupUnityAdmin)
