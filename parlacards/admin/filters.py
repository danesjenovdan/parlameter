from datetime import datetime

from django.contrib import admin

from parladata.models.common import Mandate


class MembersListFilter(admin.SimpleListFilter):
    title = "mandate"

    parameter_name = "mandate"

    def lookups(self, request, model_admin):
        mandates = Mandate.objects.all()
        return [(mandate.id, mandate.description) for mandate in mandates]

    def queryset(self, request, queryset):
        if self.value():
            mandate = Mandate.objects.get(id=self.value())
            from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
                datetime.now()
            )
            return queryset.filter(timestamp__range=[from_timestamp, to_timestamp])
        return queryset
