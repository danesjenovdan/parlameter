from django.contrib import admin
from django.db import models

from parladata.models import Amendment, AmendmentResult


class AmendmentAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "abbreviation",
        "timestamp",
        "timestamp_vote",
        "procedure_phase",
        "procedure_type",
        "motion",
        "legislation",
    )
    search_fields = ("uid", "abbreviation", "legislation__epa")
    list_filter = ("procedure_phase", "procedure_type")
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = (
        "motion",
        "legislation",
        "procedure_phase",
        "procedure_type",
        "mandate",
        "result",
        "proposed_by_organizations",
        "proposed_by_people",
    )


class AmendmentResultAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ("name",)


admin.site.register(Amendment, AmendmentAdmin)
admin.site.register(AmendmentResult, AmendmentResultAdmin)
