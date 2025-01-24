from collections import Counter

from django.conf import settings
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from parladata.admin.filters import SessionListFilter
from parladata.admin.link import LinkMotionInline
from parladata.models import *
from parladata.models.common import *
from parladata.models.task import Task
from parladata.models.versionable_properties import *


class MotionAdmin(admin.ModelAdmin):
    # form = MotionForm
    list_display = (
        "id",
        "title",
        "session_name",
        "result",
        "requirement",
        "get_for",
        "get_against",
        "get_abstain",
        "get_not",
        "link_to_vote",
        "datetime",
        "created_at",
        "tag_list",
    )
    autocomplete_fields = ("session", "champions", "agenda_items", "law")

    list_editable = ("result",)
    list_filter = (
        SessionListFilter,
        "result",
        "datetime",
    )
    search_fields = ["text", "title"]
    inlines = [
        LinkMotionInline,
    ]
    list_per_page = 25
    readonly_fields = ["created_at", "updated_at"]

    # set order of fields in the dashboard
    fields = [
        "title",
        "session",
        "datetime",
        "result",
        "agenda_items",
        "law",
        "champions",
        "summary",
        "text",
        "classification",
        "requirement",
        "parser_names",
        "tags",
    ]

    def get_queryset(self, request):
        return Motion.objects.all().prefetch_related("session", "vote").order_by("-id")

    def get_for(self, obj):
        results = dict(
            Counter(
                Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True)
            )
        ).get("for", 0)
        return results

    def get_against(self, obj):
        results = dict(
            Counter(
                Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True)
            )
        ).get("against", 0)
        return results

    def get_abstain(self, obj):
        results = dict(
            Counter(
                Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True)
            )
        ).get("abstain", 0)
        return results

    def get_not(self, obj):
        results = dict(
            Counter(
                Ballot.objects.filter(vote__motion=obj).values_list("option", flat=True)
            )
        ).get("absent", 0)
        return results

    def link_to_vote(self, obj):
        try:
            link = reverse("admin:parladata_vote_change", args=[obj.vote.first().id])
        except:
            return ""
        return mark_safe(f'<a href="{link}">Vote</a>')

    def session_name(self, obj):
        return obj.session.name if obj.session else ""

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

    link_to_vote.allow_tags = True

    get_for.short_description = "for"
    get_against.short_description = "against"
    get_abstain.short_description = "abstain"
    get_not.short_description = "absent"


admin.site.register(Motion, MotionAdmin)
