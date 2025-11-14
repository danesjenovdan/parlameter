from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from parladata.admin.link import LinkOrganizationInline
from parladata.forms import VersionableValidatorInlineFormset
from parladata.models import Link, Organization, PersonMembership
from parladata.models.versionable_properties import *


class OrganizationNameInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = OrganizationName
    extra = 0


class OrganizationAcronymInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = OrganizationAcronym
    extra = 0


class OrganizationEmailInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = OrganizationEmail
    extra = 0


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        # LinkPersonInline,
        OrganizationNameInline,
        OrganizationAcronymInline,
        OrganizationEmailInline,
        LinkOrganizationInline,
    ]
    search_fields = (
        "id",
        "organizationname__value",
        "gov_id",
    )  # Added gov_id for better search

    list_display = ("id", "get_name", "gov_id", "classification")
    autocomplete_fields = ("parent",)

    # set order of fields in the dashboard
    # fields = ['name', 'acronym', 'email', 'classification', 'parser_names', 'gov_id', 'parent', 'founding_date', 'dissolution_date', 'description', 'color', 'tags']
    fields = [
        "classification",
        "gov_id",
        "parent",
        "founding_date",
        "dissolution_date",
        "description",
        "color",
        "tags",
        "parser_names",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at"]

    # workaround made field name orderable because the name @property and is annotated
    def get_name(self, obj):
        return obj.name

    get_name.admin_order_field = "latest_name"
    get_name.short_description = "Name"


class ParliamentaryGroup(Organization):
    class Meta:
        proxy = True


class ParliamentaryGroupAdmin(OrganizationAdmin):
    list_display = ("id", "name", "tfidf", "join_organizations")

    def get_queryset(self, request):
        group_ids = PersonMembership.objects.filter(role="voter").values_list(
            "on_behalf_of", flat=True
        )
        qs = Organization.objects.filter(id__in=group_ids)
        return qs

    def tfidf(self, obj):
        partial_url = reverse("admin:parlacards_grouptfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?organization={obj.id}"
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    def join_organizations(self, obj):
        partial_url = "/admin/parladata/parliamentarygroup/mergeorganizations/"
        url = f"{settings.BASE_URL}{partial_url}?real_organization={obj.id}"
        return mark_safe(
            f'<a href="{url}"><input type="button" value="Join orgs" /></a>'
        )

    join_organizations.allow_tags = True
    join_organizations.short_description = "Join ORGS"

    tfidf.allow_tags = True
    tfidf.short_description = "TFIDF"


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(ParliamentaryGroup, ParliamentaryGroupAdmin)
