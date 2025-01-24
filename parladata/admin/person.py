from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin

from export.resources.misc import MPResource
from parladata.admin.link import LinkPersonSocialInline
from parladata.forms import VersionableValidatorInlineFormset
from parladata.models import Person, PersonMembership
from parladata.models.versionable_properties import *


class PersonNameInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonName
    extra = 0


class PersonHonorificPrefixInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonHonorificPrefix
    extra = 0


class PersonHonorificSuffixInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonHonorificSuffix
    extra = 0


class PersonPreferredPronounInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonPreferredPronoun
    extra = 0


class PersonEducationInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonEducation
    extra = 0


class PersonEducationLevelInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonEducationLevel
    extra = 0


class PersonPreviousOccupationInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonPreviousOccupation
    extra = 0


class PersonNumberOfMandatesInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonNumberOfMandates
    extra = 0


class PersonNumberOfVotersInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonNumberOfVoters
    extra = 0


class PersonEmailInline(admin.TabularInline):
    formset = VersionableValidatorInlineFormset
    model = PersonEmail
    extra = 0


# class LinkPersonInline(admin.admin.TabularInline):
#     model = Link
#     fk_name = 'person'
#     exclude = ['organization', 'membership', 'motion', 'session', 'question']
#     extra = 0


class PersonAdmin(admin.ModelAdmin):
    inlines = [
        # LinkPersonInline,
        PersonNameInline,
        PersonHonorificPrefixInline,
        PersonHonorificSuffixInline,
        PersonPreferredPronounInline,
        PersonEducationInline,
        PersonEducationLevelInline,
        PersonPreviousOccupationInline,
        PersonNumberOfMandatesInline,
        PersonNumberOfVotersInline,
        PersonEmailInline,
        LinkPersonSocialInline,
    ]
    autocomplete_fields = ["districts"]
    search_fields = ("id", "personname__value", "parser_names")
    list_display = ("id", "get_name")
    readonly_fields = ["created_at", "updated_at", "parser_names"]

    # workaround made field name orderable because the name @property and is annotated
    def get_name(self, obj):
        return obj.name

    get_name.admin_order_field = "latest_name"
    get_name.short_description = "Name"


class ParliamentMember(Person):
    class Meta:
        proxy = True


class MPAdmin(ExportMixin, PersonAdmin):
    resource_class = MPResource
    import_export_change_list_template = (
        "admin/parladata/parliamentmember/change_list.html"
    )
    list_display = ["id", "get_name", "tfidf", "join_people"]

    def get_queryset(self, request):
        MPs_ids = PersonMembership.objects.filter(role="voter").values_list(
            "member", flat=True
        )
        qs = Person.objects.filter(id__in=MPs_ids)
        return qs

    def tfidf(self, obj):
        partial_url = reverse("admin:parlacards_persontfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?member={obj.id}"
        return mark_safe(f'<a href="{url}"><input type="button" value="Tfidf" /></a>')

    def join_people(self, obj):
        partial_url = "/admin/parladata/parliamentmember/mergepeople/"
        url = f"{settings.BASE_URL}{partial_url}?real_person={obj.id}"
        return mark_safe(
            f'<a href="{url}"><input type="button" value="Join people" /></a>'
        )

    # workaround made field name orderable because the name @property and is annotated
    def get_name(self, obj):
        return obj.name

    get_name.admin_order_field = "latest_name"
    get_name.short_description = "Name"

    tfidf.allow_tags = True
    tfidf.short_description = "TFIDF"

    join_people.allow_tags = True
    join_people.short_description = "Join people"


admin.site.register(Person, PersonAdmin)
admin.site.register(ParliamentMember, MPAdmin)
