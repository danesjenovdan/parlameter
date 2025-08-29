from django.db import models
from django.utils.translation import gettext_lazy as _
from parladata.behaviors.models import Timestampable

QUESTION_TYPES = [
    ("question", "question"),
    ("initiative", "initiative"),
    ("unknown", "unknown"),
]


class Question(Timestampable):
    """All questions from members of parlament."""

    session = models.ForeignKey(
        _("Session"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Session"),
        help_text=_("Select the session this question belongs to."),
    )

    mandate = models.ForeignKey(
        _("Mandate"),
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.SET_NULL,
        verbose_name=_("Mandate"),
        help_text=_("Select the mandate of this question."),
    )

    timestamp = models.DateTimeField(
        _("timestamp"),
        blank=True,
        null=True,
        help_text=_("Select the date of the question."),
    )

    answer_timestamp = models.DateTimeField(
        _("answer_timestamp"),
        blank=True,
        null=True,
        help_text=_("Select the date of the answer to the question."),
    )

    title = models.TextField(
        _("title"),
        blank=True,
        null=True,
        help_text=_("Insert the title as written on dz-rs.si"),
    )

    person_authors = models.ManyToManyField(
        "person_authors",
        blank=True,
        related_name="authored_questions",
        verbose_name=_("Person authors"),
        help_text=_("Select the persons (MP) who asked the question."),
    )

    organization_authors = models.ManyToManyField(
        "organization_authors",
        blank=True,
        help_text=_("Select the organization that asked the question."),
        related_name="questions_org_author",
        verbose_name=_("Organization authors"),
    )

    recipient_people = models.ManyToManyField(
        "recipient_people",
        blank=True,
        help_text=_(
            "Select the recipient person (if the questions was addressed to a person)."
        ),
        related_name="received_questions",
        verbose_name=_("Recipient people"),
    )

    recipient_organizations = models.ManyToManyField(
        "recipient_organizations",
        blank=True,
        help_text=_(
            "Select the recipient organization (if the question was addressed to an organization)."
        ),
        related_name="questions_org",
        verbose_name=_("Recipient organization"),
    )

    recipient_text = models.TextField(
        _("recipient_text"),
        blank=True,
        null=True,
        help_text=_("Insert the recipient name as written on dz-rs.si"),
    )

    type_of_question = models.TextField(
        _("type_of_question"),
        blank=True,
        null=True,
        help_text=_("Select the type of question."),
        choices=QUESTION_TYPES,
    )

    gov_id = models.TextField(
        _("gov_id"),
        blank=True,
        null=True,
        help_text=_(
            "Insert the unique identifier of question, found on the government site."
        ),
    )

    def __str__(self):
        person_author_names = " ".join(
            [author.name for author in self.person_authors.all()]
        )
        organization_author_names = " ".join(
            [author.name for author in self.organization_authors.all()]
        )
        author = (
            person_author_names if person_author_names else organization_author_names
        )
        return f"{self.type_of_question}: {self.title} - {author}"


class Answer(Timestampable):
    """All questions from members of parlament."""

    question = models.ForeignKey(
        _("Question"),
        on_delete=models.CASCADE,
        verbose_name=_("Question"),
        help_text=_("Select the question this answer belongs to."),
        related_name="answers",
    )

    timestamp = models.DateTimeField(
        _("timestamp"), blank=True, null=True, help_text="Date of the question."
    )

    text = models.TextField(
        _("text"),
        blank=True,
        null=True,
        help_text="Insert the title as written on dz-rs.si",
    )

    person_authors = models.ManyToManyField(
        "Person",
        blank=True,
        related_name="authored_ansewrs",
        verbose_name=_("Person"),
        help_text=_("Select the persons (MP) who asked the question."),
    )

    organization_authors = models.ManyToManyField(
        "Organization",
        blank=True,
        help_text=_(
            "Select the recipient organization (if the question was addressed to an organization)."
        ),
        related_name="answers_org_author",
        verbose_name=_("Organization"),
    )

    def __str__(self):
        return self.text[:50]
