from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db import models

from parladata.admin.filters import SessionListFilter
from parladata.models import AgendaItem, Link


class LinkAgendaItemInline(admin.TabularInline):
    model = Link
    fk_name = "agenda_item"
    exclude = [
        "person",
        "organization",
        "motion",
        "session",
        "membership",
        "question",
        "legislation_consideration",
    ]
    extra = 0


class AgendaItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [LinkAgendaItemInline]
    list_display = ("name", "session", "order")
    list_filter = (SessionListFilter,)
    search_fields = ["name", "session__name"]
    autocomplete_fields = ["session"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ("order",)
    list_per_page = 25

    class Media:
        css = {"all": ("css/admin-extra.css",)}


admin.site.register(AgendaItem, AgendaItemAdmin)
