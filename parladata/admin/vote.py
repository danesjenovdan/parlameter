from collections import Counter

from django.conf import settings
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from import_export.admin import ExportMixin

from export.resources.session import VoteResource
from parladata.models import Vote


@admin.action(description="Clone vote with ballots")
def clone_vote(modeladmin, request, queryset):
    if queryset.count() == 1:
        vote = queryset.first()
        ballots = vote.ballots.all()
        new_vote = Vote()
        new_vote.save()
        for ballot in ballots:
            ballot.id = None
            ballot.vote = new_vote
            ballot.save()
    else:
        modeladmin.message_user(
            request, "You can only clone one vote at a time.", messages.ERROR
        )


class VoteAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = VoteResource

    list_display = (
        "name",
        "id",
        "the_tags",
        "get_for",
        "get_against",
        "get_abstain",
        "get_absent",
        "get_did_not_vote",
        "needs_editing",
        "add_ballots",
        "add_anonymous_ballots",
    )
    # set order of fields in the dashboard
    fields = [
        "name",
        "timestamp",
        "motion",
        "result",
        "needs_editing",
        "tags",
        "get_session",
        "get_statistics",
        "edit_ballots",
        "get_vote_pdf",
    ]
    readonly_fields = [
        "get_session",
        "get_statistics",
        "edit_ballots",
        "get_vote_pdf",
        "created_at",
        "updated_at",
    ]

    list_filter = ("tags",)
    inlines = [
        # CountVoteInline,
    ]
    search_fields = ["name"]

    actions = [clone_vote]

    autocomplete_fields = ("motion",)
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super(VoteAdmin, self).get_queryset(request)
        queryset = queryset.prefetch_related("ballots", "motion", "motion__session")
        return queryset

    def the_tags(self, obj):
        return "%s" % (list(obj.tags.values_list("name", flat=True)),)

    def get_session(self, obj):
        return obj.motion.session.name if obj.motion and obj.motion.session else ""

    def add_ballots(self, obj):
        partial_url = "/admin/parladata/vote/addballots/"
        url = f"{settings.BASE_URL}{partial_url}?vote_id={obj.id}"
        if not obj.ballots.all():
            return mark_safe(
                f'<a href="{url}"><input type="button" value="Add ballots" /></a>'
            )
        else:
            return ""

    def add_anonymous_ballots(self, obj):
        partial_url = "/admin/parladata/vote/addanonymousballots/"
        url = f"{settings.BASE_URL}{partial_url}?vote_id={obj.id}"
        return mark_safe(
            f'<a href="{url}"><input type="button" value="Add anonymous ballots" /></a>'
        )

    def edit_ballots(self, obj):
        change_url = reverse("admin:parladata_ballot_changelist")
        return mark_safe(
            f'<a href="{change_url}?vote__id__exact={obj.id}" target="_blank"><input type="button" value="Edit ballots" /></a>'
        )

    def get_for(self, obj):
        results = dict(Counter(obj.ballots.all().values_list("option", flat=True))).get(
            "for", 0
        )
        return results

    def get_against(self, obj):
        results = dict(Counter(obj.ballots.all().values_list("option", flat=True))).get(
            "against", 0
        )
        return results

    def get_abstain(self, obj):
        results = dict(Counter(obj.ballots.all().values_list("option", flat=True))).get(
            "abstain", 0
        )
        return results

    def get_absent(self, obj):
        results = dict(Counter(obj.ballots.all().values_list("option", flat=True))).get(
            "absent", 0
        )
        return results

    def get_did_not_vote(self, obj):
        results = dict(Counter(obj.ballots.all().values_list("option", flat=True))).get(
            "did not vote", 0
        )
        return results

    def get_vote_pdf(self, obj):
        vote_pdf = (
            obj.motion.links.filter(tags__name="vote-pdf")
            .values_list("url", flat=True)
            .first()
        )
        if vote_pdf:
            return mark_safe(
                f'<a href="{vote_pdf}" target="_blank"><input type="button" value="Vote pdf" /></a>'
            )
        else:
            return ""

    def get_statistics(self, obj):
        for_votes = self.get_for(obj)
        against = self.get_against(obj)
        abstain = self.get_abstain(obj)
        absent = self.get_absent(obj)
        did_not_vote = self.get_did_not_vote(obj)

        return mark_safe(
            f"""<table>
                <tr>
                    <th>{_("for")}</th>
                    <th>{_("against")}</th>
                    <th>{_("abstain")}</th>
                    <th>{_("absent")}</th>
                    <th>{_('did not vote')}</th>
                    <th>{_("all")}</th>
                </tr>
                <tr>
                    <td>{for_votes}</td>
                    <td>{against}</td>
                    <td>{abstain}</td>
                    <td>{absent}</td>
                    <td>{did_not_vote}</th>
                    <td>{for_votes + against + abstain + absent + did_not_vote}</td>
                </tr>
            </table>
            """
        )

    get_for.short_description = "for"
    get_against.short_description = "against"
    get_abstain.short_description = "abstain"
    get_absent.short_description = "absent"
    get_did_not_vote.short_description = "did not vote"
    the_tags.short_description = "tags"
    add_ballots.allow_tags = True
    add_ballots.short_description = "Add ballots"
    add_anonymous_ballots.allow_tags = True
    add_anonymous_ballots.short_description = "Add anonymous ballots"
    edit_ballots.allow_tags = True
    edit_ballots.short_description = "Edit ballots"
    get_vote_pdf.allow_tags = True
    get_vote_pdf.short_description = "Vote pdf"
    get_statistics.allow_tags = True
    get_statistics.short_description = "Statistics"
    get_session.short_description = "Session"


admin.site.register(Vote, VoteAdmin)
