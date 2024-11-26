from datetime import datetime

from django.db import models

from parladata.behaviors.models import Versionable, Timestampable, Taggable

from parlacards.scores.common import tokenize, remove_punctuation, get_lemmatize_method



class ValidSpeechesManager(models.Manager):
    def filter_valid_speeches(self, timestamp=None):
        if not timestamp:
            timestamp = datetime.now()

        return super().get_queryset().filter(
            models.Q(valid_from__lt=timestamp) | models.Q(valid_from__isnull=True),
            models.Q(valid_to__gt=timestamp) | models.Q(valid_to__isnull=True)
        )


class Speech(Versionable, Timestampable, Taggable):
    """Speeches that happened in parlament."""

    speaker = models.ForeignKey('Person',
                                on_delete=models.CASCADE,
                                related_name='speeches',
                                help_text='Person making the speech')

    content = models.TextField(blank=False, null=False, help_text='Words spoken')

    lemmatized_content = models.TextField(blank=True, null=True, help_text='Lemmatized words spoken')

    order = models.IntegerField(blank=True, null=True,
                                help_text='Order of speech')

    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                related_name='speeches',
                                help_text='Speech session')

    start_time = models.DateTimeField(blank=True, null=True,
                                     help_text='Start time')

    end_time = models.DateTimeField(blank=True, null=True,
                                   help_text='End time')

    agenda_items = models.ManyToManyField('AgendaItem', blank=True,
                                          help_text='Agenda items', related_name='speeches')

    motions = models.ManyToManyField('Motion',
                                    blank=True,
                                    help_text='Votes on speech')

    objects = ValidSpeechesManager()

    def __str__(self):
        if self.session:
            return f'{self.speaker.name} @ {self.session.name}:{self.order}'
        return f'{self.speaker.name} @ ???:{self.order}'

    def lemmatize_and_save(self):
        if self.lemmatized_content:
            return
        lemmatize_many = get_lemmatize_method('lemmatize_many')
        self.lemmatized_content = lemmatize_many(self.content)
        self.save()
    
    @staticmethod
    def lemmatize(content):
        lemmatize_many = get_lemmatize_method('lemmatize_many')
        lemmatized_content = ' '.join(
            [lemmatized_token for lemmatized_token in lemmatize_many(
                tokenize(
                    remove_punctuation(
                        content.strip()
                    )
                )
            )]
        )

        return lemmatized_content

    @property
    def agenda_item(self):
        if self.agenda_items.all().count() > 1:
            raise Exception('This session belongs to multiple agenda items. Use the plural form "agenda_items".')

        return self.agenda_items.first()

    @property
    def parliamentary_group(self):
        return self.speaker.parliamentary_group_on_date(datetime=self.start_time)

    class Meta:
        verbose_name_plural = "Speeches"

