from django.db import models

from tinymce.models import HTMLField

from parladata.behaviors.models import Timestampable, Taggable


class LegislationStatus(Timestampable):
    name = models.TextField(
        blank=True,
        null=True,
        help_text='Status of legisaltion'
    )

    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_default_photo_pk(cls):
        obj, created_bool = cls.objects.get_or_create(
            name='in_procedure'
        )
        return obj.pk


class Law(Timestampable, Taggable):
    """Laws which taken place in parlament."""
    STATUSES = [
        ('in_procedure', 'in_procedure'),
        ('enacted', 'enacted'),
        ('submitted', 'submitted'),
        ('rejected', 'rejected'),
        ('adopted', 'adopted'),
        ('received', 'received'),
        ('retracted', 'retracted'),
    ]

    uid = models.TextField(blank=True, null=True,
                           help_text='law uid from DZ page')


    session = models.ForeignKey('Session',
                                blank=True, null=True,
                                on_delete=models.CASCADE,
                                help_text='The legislative session in which the law was proposed')


    mandate = models.ForeignKey('Mandate',
                                blank=True, null=True,
                                related_name='legislation',
                                on_delete=models.SET_NULL,
                                help_text='The mandate of this law.')


    text = models.TextField(blank=True, null=True,
                            help_text='The text of the law')


    epa = models.TextField(blank=True, null=True,
                           help_text='EPA number')

    mdt = models.TextField(blank=True, null=True,
                           max_length=1024,
                           help_text='Working body text')

    mdt_fk = models.ForeignKey('Organization',
                               related_name='laws',
                               blank=True, null=True,
                               max_length=255,
                               on_delete=models.CASCADE,
                               help_text='Working body obj')

    status = models.ForeignKey(
        'LegislationStatus',
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True,
        default=LegislationStatus.get_or_create_default_photo_pk,
    )

    passed = models.BooleanField(blank=True, null=True)

    proposer_text = models.TextField(blank=True, null=True,
                                     help_text='Proposer of law')

    procedure_type = models.TextField(blank=True, null=True,
                                 max_length=255,
                                 help_text='Skrajšani, normalni, hitri postopek...')

    classification = models.ForeignKey(
        'LegislationClassification',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    abstract = HTMLField(blank=True,
                     null=True)

    timestamp = models.DateTimeField(blank=True,
                               null=True,
                               help_text='Date of the law.')

    considerations = models.ManyToManyField(
        'ProcedurePhase',
        through='LegislationConsideration',
        blank=True,
        help_text='Consideration of legislation'
    )

    def __str__(self):
        return f'{self.session.name if self.session else ""} -> {self.text}'

    @property
    def has_votes(self):
        # TODO
        return True

    @property
    def has_abstract(self):
        return bool(self.abstract)

    class Meta:
        verbose_name = 'Law'
        verbose_name_plural = 'Legislation'


class Procedure(Timestampable):
    type = models.TextField(
        blank=True,
        null=True,
        help_text='Name of procedure type'
    )


class ProcedurePhase(Timestampable):
    name = models.TextField(
        blank=True,
        null=True,
        help_text='Name of procedure phase'
    )
    procedure = models.ForeignKey(
        'Procedure',
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.name


class LegislationConsideration(Timestampable):
    timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Date of the law.'
    )
    organization = models.ForeignKey(
        'Organization',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text='Organization in which consideration happened'
    )
    legislation = models.ForeignKey(
        'Law',
        on_delete=models.CASCADE
    )
    procedure_phase = models.ForeignKey(
        'ProcedurePhase',
        on_delete=models.CASCADE
    )
    session = models.ForeignKey('Session',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='legislation_considerations',
        help_text='Session at which the legislation was discussed'
    )


class LegislationClassification(Timestampable):
    name = models.TextField(
        blank=True,
        null=True,
        help_text='Status of legisaltion'
    )

    def __str__(self):
        return self.name
