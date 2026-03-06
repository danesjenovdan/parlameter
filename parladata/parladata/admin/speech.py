from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.db import models

from parladata.admin.filters import SessionListFilter
from parladata.models.motion import Motion
from parladata.models.speech import Speech


@admin.action(description="Duplicate selected speeches")
def duplicate_speech(modeladmin, request, queryset):
    if queryset.count() == 1:
        for speech in queryset:
            # first, move all consecutive speeches forward for one order
            # TODO this is a bit inefficient, maybe problematic for LONG sessions
            speeches_to_move = Speech.objects.filter(
                session=speech.session,
                order__gt=speech.order,
            )
            for speech_to_move in speeches_to_move:
                speech_to_move.order += 1
                speech_to_move.save()

            # clear lemmatized_content for the speech
            speech.lemmatized_content = None
            speech.save()

            # make a copy of the speech and increment its order
            speech.pk = None
            speech.order += 1
            speech.save()
    else:
        modeladmin.message_user(
            request, "You can only duplicate one speech at a time.", messages.ERROR
        )


class ValidSpeechFilter(admin.SimpleListFilter):
    title = "valid speech"
    parameter_name = "valid"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Valid"),
            ("no", "Invalid"),
        ]

    def queryset(self, request, queryset):
        timestamp = datetime.now()
        if self.value() == "yes":
            return queryset.filter(
                models.Q(valid_from__lt=timestamp) | models.Q(valid_from__isnull=True),
                models.Q(valid_to__gt=timestamp) | models.Q(valid_to__isnull=True),
            )
        elif self.value() == "no":
            return queryset.exclude(
                models.Q(valid_from__lt=timestamp) | models.Q(valid_from__isnull=True),
                models.Q(valid_to__gt=timestamp) | models.Q(valid_to__isnull=True),
            )


class SpeechForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["motions"].queryset = Motion.objects.filter(
            session=self.instance.session
        )


class SpeechAdmin(admin.ModelAdmin):
    form = SpeechForm
    fields = [
        "session",
        "content",
        "speaker",
        "order",
        "motions",
        "start_time",
        "tags",
        "lemmatized_content",
    ]
    list_filter = (ValidSpeechFilter, "tags", SessionListFilter)
    search_fields = ["speaker__personname__value", "content"]
    autocomplete_fields = ["motions", "speaker", "session"]
    inlines = []
    list_display = (
        "id",
        "order",
        "is_valid",
        "tag_list",
        "session_name",
        "speaker",
    )
    ordering = ("order",)
    list_per_page = 25
    formfield_overrides = {
        models.ManyToManyField: {"widget": forms.CheckboxSelectMultiple()},
    }
    actions = [duplicate_speech]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("tags", "session", "speaker")
        )

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

    def session_name(self, obj):
        if obj.session:
            return obj.session.name
        return "Speech has no session"

    def is_valid(self, obj):
        timestamp = datetime.now()
        valid_from = obj.valid_from is None or obj.valid_from < timestamp
        valid_to = obj.valid_to is None or obj.valid_to > timestamp
        return valid_from and valid_to

    is_valid.boolean = True
    is_valid.short_description = "Valid"


admin.site.register(Speech, SpeechAdmin)
