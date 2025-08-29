from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Taggable, Timestampable


class LegislationStatus(Timestampable):
    name = models.TextField(
        _("Name"), blank=True, null=True, help_text=_("Status of legisaltion")
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_default_photo_pk(cls):
        obj, created_bool = cls.objects.get_or_create(name="in_procedure")
        return obj.pk


class Law(Timestampable, Taggable):
    """Laws which taken place in parlament."""

    STATUSES = [
        ("in_procedure", "in_procedure"),
        ("enacted", "enacted"),
        ("submitted", "submitted"),
        ("rejected", "rejected"),
        ("adopted", "adopted"),
        ("received", "received"),
        ("retracted", "retracted"),
    ]

    uid = models.TextField(
        _("uid"),
        blank=True,
        null=True,
        help_text=_("uid reference of the law found on the DZ page"),
    )

    session = models.ForeignKey(
        _("Session"),
        blank=True,
        null=True,
        verbose_name=_("Session"),
        on_delete=models.CASCADE,
        help_text=_(
            "The legislative session in which the law was proposed",
        ),
    )

    mandate = models.ForeignKey(
        _("Mandate"),
        blank=True,
        null=True,
        verbose_name=_("Mandate"),
        related_name="legislation",
        on_delete=models.SET_NULL,
        help_text=_("Select the mandate of the law."),
    )

    text = models.TextField(
        _("text"),
        blank=True,
        null=True,
        help_text=_("Insert the title of the law eg. 'Zakon o...'"),
    )

    epa = models.TextField(
        _("EPA"),
        blank=True,
        null=True,
        help_text=_("Insert the EPA number eg. 2318-IX"),
    )

    mdt = models.TextField(
        _("MDT"),
        blank=True,
        null=True,
        max_length=1024,
        help_text=_("Insert the working body eg. 'Committee on the Economy'"),
    )

    mdt_fk = models.ForeignKey(
        _("Organization"),
        related_name="laws",
        blank=True,
        null=True,
        verbose_name=_("Organization"),
        max_length=255,
        on_delete=models.CASCADE,
        help_text=_("Select the working body"),
    )

    status = models.ForeignKey(
        _("LegislationStatus"),
        on_delete=models.SET_DEFAULT,
        blank=True,
        null=True,
        verbose_name=_("Legislation status"),
        help_text=_("Select the status of the legislative procedure"),
        default=LegislationStatus.get_or_create_default_photo_pk,
    )

    passed = models.BooleanField(blank=True, null=True)

    proposer_text = models.TextField(
        _("proposer_text"),
        blank=True,
        null=True,
        help_text=_("Insert who proposed the law"),
    )

    procedure_type = models.TextField(
        _("procedure_type"),
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Insert the type of procedure (redni, skrajšani, nujni)"),
    )

    classification = models.ForeignKey(
        "LegislationClassification",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Legislation classification"),
    )

    abstract = HTMLField(blank=True, null=True)

    timestamp = models.DateTimeField(
        blank=True, null=True, help_text="Date of the law."
    )

    considerations = models.ManyToManyField(
        "ProcedurePhase",
        through="LegislationConsideration",
        blank=True,
        help_text="Consideration of legislation",
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
        verbose_name = "Law"
        verbose_name_plural = "Legislation"


class Procedure(Timestampable):
    type = models.TextField(blank=True, null=True, help_text="Name of procedure type")


class ProcedurePhase(Timestampable):
    name = models.TextField(blank=True, null=True, help_text="Name of procedure phase")
    procedure = models.ForeignKey(
        "Procedure",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class LegislationConsideration(Timestampable):
    timestamp = models.DateTimeField(
        blank=True, null=True, help_text="Date of the law."
    )
    organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        verbose_name=_("Organization"),
        on_delete=models.CASCADE,
        help_text="Organization in which consideration happened",
    )
    legislation = models.ForeignKey("Law", on_delete=models.CASCADE)
    procedure_phase = models.ForeignKey("ProcedurePhase", on_delete=models.CASCADE)
    session = models.ForeignKey(
        "Session",
        blank=True,
        null=True,
        verbose_name=_("Session"),
        on_delete=models.CASCADE,
        related_name="legislation_considerations",
        help_text="Session at which the legislation was discussed",
    )


class LegislationClassification(Timestampable):
    name = models.TextField(blank=True, null=True, help_text="Status of legisaltion")

    def __str__(self):
        return self.name
