from django.db import models
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Taggable, Timestampable


class LegislationStatus(Timestampable):
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("Status of legislation for example 'in_procedure', 'enacted'..."),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Legislation status")
        verbose_name_plural = _("Legislation statuses")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_default_photo_pk(cls):
        obj, created_bool = cls.objects.get_or_create(name="in_procedure")
        return obj.pk


class Law(Timestampable, Taggable):
    """Laws which taken place in parlament."""

    uid = models.TextField(
        verbose_name=_("uid"),
        help_text=_("uid reference of the law found on the source page"),
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("The legislative session in which the law was proposed"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    mandate = models.ForeignKey(
        "Mandate",
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of the law."),
        blank=True,
        null=True,
        related_name="legislation",
        on_delete=models.SET_NULL,
    )
    text = models.TextField(
        verbose_name=_("text"),
        help_text=_("Insert the text of the law eg. 'Law on...'"),
        blank=True,
        null=True,
    )
    epa = models.TextField(
        verbose_name=_("EPA"),
        help_text=_("Insert the EPA number eg. 2318-IX"),
        blank=True,
        null=True,
    )
    mdt = models.TextField(
        verbose_name=_("MDT"),
        help_text=_("Insert the working body eg. 'Committee on the Economy'"),
        blank=True,
        null=True,
        max_length=1024,
    )
    mdt_fk = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("Select the working body"),
        related_name="laws",
        blank=True,
        null=True,
        max_length=255,
        on_delete=models.CASCADE,
    )

    status = models.ForeignKey(
        "LegislationStatus",
        verbose_name=_("Legislation status"),
        help_text=_("Select the status of the legislative procedure"),
        blank=True,
        null=True,
        on_delete=models.SET_DEFAULT,
        default=LegislationStatus.get_or_create_default_photo_pk,
    )
    passed = models.BooleanField(
        verbose_name=_("passed"),
        help_text=_("Was the law passed?"),
        blank=True,
        null=True,
        default=False,
    )
    proposer_text = models.TextField(
        verbose_name=_("proposer_text"),
        help_text=_("Insert who proposed the law"),
        blank=True,
        null=True,
    )
    procedure_type = models.TextField(
        verbose_name=_("procedure_type"),
        help_text=_("Insert the type of procedure (e.g., 'regular', 'urgent'...)"),
        blank=True,
        null=True,
        max_length=255,
    )
    classification = models.ForeignKey(
        "LegislationClassification",
        verbose_name=_("Legislation classification"),
        help_text=_("Classification of legislation (e.g., 'Law', 'Act', 'Decree'...)"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    abstract = HTMLField(
        verbose_name=_("Abstract"),
        help_text=_("Abstract of the law in HTML"),
        blank=True,
        null=True,
    )
    timestamp = models.DateTimeField(
        verbose_name=_("Timestamp"),
        help_text=_("Date of the law."),
        blank=True,
        null=True,
    )
    considerations = models.ManyToManyField(
        "ProcedurePhase",
        verbose_name=_("Considerations"),
        help_text=_("Consideration of legislation"),
        through="LegislationConsideration",
        blank=True,
    )

    @property
    def has_votes(self):
        # TODO
        return True

    @property
    def has_abstract(self):
        return bool(self.abstract)

    class Meta:
        verbose_name = _("Law")
        verbose_name_plural = _("Legislation")

    def __str__(self):
        return f'{self.session.name if self.session else ""} -> {self.text}'


class Procedure(Timestampable):
    type = models.TextField(
        verbose_name=_("Type"),
        help_text=_("Name of procedure type"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Procedure")
        verbose_name_plural = _("Procedures")


class ProcedurePhase(Timestampable):
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("Name of procedure phase"),
        blank=True,
        null=True,
    )
    procedure = models.ForeignKey(
        "Procedure",
        verbose_name=_("Procedure"),
        help_text=_("Procedure to which the phase belongs"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Procedure phase")
        verbose_name_plural = _("Procedure phases")

    def __str__(self):
        return self.name


class LegislationConsideration(Timestampable):
    timestamp = models.DateTimeField(
        verbose_name=_("Timestamp"),
        help_text=_("Date of the law."),
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        "Organization",
        verbose_name=_("Organization"),
        help_text=_("Organization in which consideration happened"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    legislation = models.ForeignKey(
        "Law",
        verbose_name=_("Legislation"),
        help_text=_("Legislation that was considered"),
        on_delete=models.CASCADE,
    )
    procedure_phase = models.ForeignKey(
        "ProcedurePhase",
        verbose_name=_("Procedure phase"),
        help_text=_("Phase of the procedure"),
        on_delete=models.CASCADE,
    )
    session = models.ForeignKey(
        "Session",
        verbose_name=_("Session"),
        help_text=_("Session at which the legislation was discussed"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="legislation_considerations",  
    )

    class Meta:
        verbose_name = _("Legislation consideration")
        verbose_name_plural = _("Legislation considerations")
        ordering = ["-timestamp"]


class LegislationClassification(Timestampable):
    name = models.TextField(
        verbose_name=_("Name"),
        help_text=_("Classification of legislation (e.g., 'Law', 'Act', 'Decree'...)"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Legislation classification")
        verbose_name_plural = _("Legislation classifications")
        ordering = ["name"]

    def __str__(self):
        return self.name
