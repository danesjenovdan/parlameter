from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from parladata.admin.filters import SessionOrganizationsListFilter
from parladata.models import Link, Session


class SessionLinkInline(admin.TabularInline):
    model = Link
    fk_name = "session"
    exclude = [
        "person",
        "membership",
        "motion",
        "question",
        "organization",
        "agenda_item",
        "answer",
        "legislation_consideration",
    ]
    extra = 0


class SessionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["mandate", "organizations"]
    inlines = [
        SessionLinkInline
        # SpeechSessionInline,
        # MotionSessionInline,
    ]
    search_fields = ["name"]
    list_display = [
        "id",
        "name",
        "tfidf",
        "run_tfidf",
        "agenda_items",
        "start_time",
        "in_review",
        "get_mandate",
        "get_organizations",
    ]
    readonly_fields = ["created_at", "updated_at"]
    list_filter = ("mandate", SessionOrganizationsListFilter)

    list_per_page = 25

    def tfidf(self, obj):
        partial_url = reverse("admin:parlacards_sessiontfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?session__id__exact={obj.id}"
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    def run_tfidf(self, obj):
        url = reverse("session_tfidf_task", kwargs={"session": obj.id})
        return mark_safe(
            f'<a href="{url}"><input type="button" value="Run TFIDF task" /></a>'
        )

    def get_mandate(self, obj):
        return obj.mandate.description

    def get_organizations(self, obj):
        return " - ".join([org.name for org in obj.organizations.all()])

    tfidf.allow_tags = True
    tfidf.short_description = "TFIDF"
    run_tfidf.allow_tags = True
    run_tfidf.short_description = "TFIDF TASK"
    get_mandate.short_description = "mandate"
    get_organizations.short_description = "Organizations"

    def agenda_items(self, obj):
        partial_url = reverse("admin:parladata_agendaitem_changelist")
        url = f"{settings.BASE_URL}{partial_url}?session__id__exact={obj.id}"
        return mark_safe(
            f'<a href="{url}"><input type="button" value="Agenda items" /></a>'
        )

    agenda_items.allow_tags = True
    agenda_items.short_description = "Agenda items"


admin.site.register(Session, SessionAdmin)
