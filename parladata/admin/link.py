from django.contrib import admin
from django.forms import ChoiceField, ModelForm

from parladata.admin.filters import ParsableFilter
from parladata.models.link import Link

PERSON_SOCIAL_NETWORK_CHOICES = (
    ("", ""),
    ("facebook", "facebook"),
    ("twitter", "twitter"),
    ("linkedin", "linkedin"),
    ("instagram", "instagram"),
    ("tiktok", "tiktok"),
)

ORGANIZATION_LINK_CHOICES = (
    ("", ""),
    ("budget", "budget"),
    ("website", "website"),
    ("facebook", "facebook"),
    ("twitter", "twitter"),
    ("linkedin", "linkedin"),
)

MOTION_LINK_CHOICES = (
    ("", ""),
    ("analyse", "analyse"),
)


class SocialForm(ModelForm):
    note = ChoiceField(choices=PERSON_SOCIAL_NETWORK_CHOICES)

    class Meta:
        model = Link
        exclude = [
            "question",
            "organization",
            "motion",
            "session",
            "membership",
            "agenda_item",
            "legislation_consideration",
            "answer",
        ]


class OrganizationLinkForm(ModelForm):
    note = ChoiceField(choices=ORGANIZATION_LINK_CHOICES)

    class Meta:
        model = Link
        exclude = [
            "person",
            "membership",
            "motion",
            "question",
            "session",
            "agenda_item",
            "legislation_consideration",
            "answer",
        ]


class MotionLinkForm(ModelForm):
    note = ChoiceField(choices=MOTION_LINK_CHOICES)

    class Meta:
        model = Link
        exclude = [
            "person",
            "membership",
            "organization",
            "session",
            "question",
            "agenda_item",
            "legislation_consideration",
            "answer",
        ]


class LinkOrganizationInline(admin.TabularInline):
    model = Link
    form = OrganizationLinkForm
    fk_name = "organization"
    exclude = [
        "person",
        "membership",
        "motion",
        "question",
        "session",
        "agenda_item",
        "legislation_consideration",
        "answer",
    ]
    extra = 0


class LinkMembershipInline(admin.TabularInline):
    model = Link
    fk_name = "membership"
    exclude = [
        "person",
        "organization",
        "motion",
        "question",
        "session",
        "agenda_item",
        "legislation_consideration",
        "answer",
    ]
    extra = 0


class LinkMotionInline(admin.TabularInline):
    model = Link
    form = MotionLinkForm
    fk_name = "motion"
    exclude = [
        "person",
        "membership",
        "organization",
        "session",
        "question",
        "agenda_item",
        "legislation_consideration",
        "answer",
    ]
    extra = 0


class LinkQuestionInline(admin.TabularInline):
    model = Link
    fk_name = "question"
    exclude = [
        "person",
        "organization",
        "motion",
        "session",
        "membership",
        "agenda_item",
        "legislation_consideration",
        "answer",
    ]
    extra = 0


class LinkAnswerInline(admin.TabularInline):
    model = Link
    fk_name = "answer"
    exclude = [
        "person",
        "organization",
        "motion",
        "session",
        "membership",
        "agenda_item",
        "legislation_consideration",
        "question",
    ]
    extra = 0


class LinkPersonSocialInline(admin.TabularInline):
    model = Link
    form = SocialForm
    fk_name = "person"
    exclude = [
        "question",
        "organization",
        "motion",
        "session",
        "membership",
        "agenda_item",
        "legislation_consideration",
        "answer",
    ]
    extra = 0


class LinkAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    autocomplete_fields = [
        "session",
        "person",
        "motion",
        "question",
        "agenda_item",
        "organization",
        "membership",
        "answer",
    ]
    fields = [
        "url",
        "name",
        "tags",
        "session",
        "agenda_item",
        "motion",
        "question",
        "person",
        "organization",
        "membership",
        "date",
        "note",
        "answer",
    ]
    readonly_fields = ["created_at", "updated_at"]
    list_filter = (ParsableFilter,)


admin.site.register(Link, LinkAdmin)
