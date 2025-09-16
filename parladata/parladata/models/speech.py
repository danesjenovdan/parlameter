from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.db import models

from parlacards.scores.common import get_lemmatize_method, remove_punctuation, tokenize
from parladata.behaviors.models import Taggable, Timestampable, Versionable


class ValidSpeechesManager(models.Manager):
    def filter_valid_speeches(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return (
            super()
            .get_queryset()
            .filter(
                models.Q(valid_from__lt=timestamp) | models.Q(valid_from__isnull=True),
                models.Q(valid_to__gt=timestamp) | models.Q(valid_to__isnull=True),
            )
        )


class Speech(Versionable, Timestampable, Taggable):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey(
        "Person",
        verbose_name=_("Speaker"),
        help_text=_("Select the person making the speech"),
        on_delete=models.CASCADE,
        related_name="speeches",
    )
    content = models.TextField(
        verbose_name=_("content"),
        help_text=_("The content of the speech."),
        blank=False,
        null=False,
    )
    lemmatized_content = models.TextField(
        verbose_name=_("lemmatized_content"),
        help_text=_("Lemmatized words spoken"),
        blank=True,
        null=True,
    )
    order = models.IntegerField(
        verbose_name=_("order"),
        help_text=_("Order of the speech"),
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("Select the session of the speech."),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="speeches",
    )
    start_time = models.DateTimeField(
        verbose_name=_("start_time"),
        help_text=_("Select the start time"),
        blank=True,
        null=True,
    )
    end_time = models.DateTimeField(
        verbose_name=_("end_time"),
        help_text=_("Select the end time"),
        blank=True,
        null=True,
    )
    agenda_items = models.ManyToManyField(
        "AgendaItem",
        verbose_name=_("Agenda items"),
        help_text=_("Select agenda items"),
        blank=True,
        related_name="speeches",
    )
    motions = models.ManyToManyField(
        "Motion",
        verbose_name=_("Motions"),
        help_text=_("Select motions related to the speech"),
        blank=True,
    )
    objects = ValidSpeechesManager()

    class Meta:
        verbose_name = "Speech"
        verbose_name_plural = "Speeches"

    def __str__(self):
        if self.session:
            return f"{self.speaker.name} @ {self.session.name}:{self.order}"
        return f"{self.speaker.name} @ ???:{self.order}"

    def lemmatize_and_save(self):
        if self.lemmatized_content:
            return
        lemmatize_many = get_lemmatize_method("lemmatize_many")
        self.lemmatized_content = lemmatize_many(self.content)
        self.save()

    @staticmethod
    def lemmatize(content):
        lemmatize_many = get_lemmatize_method("lemmatize_many")
        lemmatized_content = " ".join(
            [
                lemmatized_token
                for lemmatized_token in lemmatize_many(
                    tokenize(remove_punctuation(content.strip()))
                )
            ]
        )

        return lemmatized_content

    @property
    def agenda_item(self):
        if self.agenda_items.all().count() > 1:
            raise Exception(
                'This session belongs to multiple agenda items. Use the plural form "agenda_items".'
            )

        return self.agenda_items.first()

    @property
    def parliamentary_group(self):
        return self.speaker.parliamentary_group_on_date(datetime=self.start_time)
