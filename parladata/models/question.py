from django.db import models

from parladata.behaviors.models import Timestampable

QUESTION_TYPES = [
    ("question", "question"),
    ("initiative", "initiative"),
    ("unknown", "unknown"),
]


class Question(Timestampable):
    """All questions from members of parlament."""

    session = models.ForeignKey(
        "Session",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The session this question belongs to.",
    )

    mandate = models.ForeignKey(
        "Mandate",
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.SET_NULL,
        help_text="The mandate of this question.",
    )

    timestamp = models.DateTimeField(
        blank=True, null=True, help_text="Date of the question."
    )

    answer_timestamp = models.DateTimeField(
        blank=True, null=True, help_text="Date of answer the question."
    )

    title = models.TextField(
        blank=True, null=True, help_text="Title name as written on dz-rs.si"
    )

    person_authors = models.ManyToManyField(
        "Person",
        blank=True,
        related_name="authored_questions",
        help_text="The persons (MP) who asked the question.",
    )

    organization_authors = models.ManyToManyField(
        "Organization",
        blank=True,
        help_text="Recipient organization (if it's an organization).",
        related_name="questions_org_author",
    )

    recipient_people = models.ManyToManyField(
        "Person",
        blank=True,
        help_text="Recipient person (if it's a person).",
        related_name="received_questions",
    )

    recipient_organizations = models.ManyToManyField(
        "Organization",
        blank=True,
        help_text="Recipient organization (if it's an organization).",
        related_name="questions_org",
    )

    recipient_text = models.TextField(
        blank=True, null=True, help_text="Recipient name as written on dz-rs.si"
    )

    type_of_question = models.TextField(
        blank=True,
        null=True,
        choices=QUESTION_TYPES,
    )

    gov_id = models.TextField(
        blank=True,
        null=True,
        help_text="Unique identifier of question on government site.",
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
        "Question",
        on_delete=models.CASCADE,
        help_text="The question this answer belongs to.",
        related_name="answers",
    )

    timestamp = models.DateTimeField(
        blank=True, null=True, help_text="Date of the question."
    )

    text = models.TextField(
        blank=True, null=True, help_text="Title name as written on dz-rs.si"
    )

    person_authors = models.ManyToManyField(
        "Person",
        blank=True,
        related_name="authored_ansewrs",
        help_text="The persons (MP) who asked the question.",
    )

    organization_authors = models.ManyToManyField(
        "Organization",
        blank=True,
        help_text="Recipient organization (if it's an organization).",
        related_name="answers_org_author",
    )

    def __str__(self):
        return self.text[:50]
