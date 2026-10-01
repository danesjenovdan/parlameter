from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from parladata.admin.filters import SessionLegislationListFilter
from parladata.models import (
    Law,
    LegislationClassification,
    LegislationConsideration,
    LegislationStatus,
    Procedure,
    ProcedurePhase,
    ProcedureType,
    ProcedureTypeDefaultPhase,
)


class LegislationConsiderationInline(admin.TabularInline):
    model = LegislationConsideration
    fk_name = "legislation"
    fields = ["timestamp", "organization", "procedure_phase", "session"]
    autocomplete_fields = ("organization", "procedure_phase", "session")
    extra = 0


class LawAdmin(admin.ModelAdmin):
    list_display = ("text", "get_sessions", "status", "epa", "procedure_type")
    list_filter = (SessionLegislationListFilter,)
    search_fields = ("text", "epa")
    exclude = ("session",)
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 20
    autocomplete_fields = ("mdt_fk", "status", "classification", "considerations")

    inlines = [LegislationConsiderationInline]

    def get_sessions(self, obj):
        return list(
            obj.legislationconsideration_set.all().values_list(
                "session__name", flat=True
            )
        )

    get_sessions.short_description = "Sessions"


class ProcedureAdmin(admin.ModelAdmin):
    list_display = ("type",)
    search_fields = ("type",)
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ("name",)


class ProcedurePhaseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ("procedure",)


class LegislationConsiderationAdmin(admin.ModelAdmin):
    list_display = ("legislation", "procedure_phase", "timestamp")
    autocomplete_fields = ("legislation", "organization", "session", "procedure_phase")
    readonly_fields = ["created_at", "updated_at"]
    search_fields = ("procedure_phase__name",)


class LegislationStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)
    readonly_fields = ["created_at", "updated_at"]


class LegislationClassificationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ["created_at", "updated_at"]


class ProcedureTypeDefaultPhaseInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProcedureTypeDefaultPhase
    fk_name = "procedure_type"
    fields = ["procedure_phase", "order"]
    extra = 0
    readonly_fields = ["created_at", "updated_at"]


class ProcedureTypeAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProcedureTypeDefaultPhaseInline]


admin.site.register(Law, LawAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(ProcedurePhase, ProcedurePhaseAdmin)
admin.site.register(LegislationConsideration, LegislationConsiderationAdmin)
admin.site.register(LegislationStatus, LegislationStatusAdmin)
admin.site.register(LegislationClassification, LegislationClassificationAdmin)
admin.site.register(ProcedureType, ProcedureTypeAdmin)
