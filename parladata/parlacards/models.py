from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


# Create your models here.
class Score(Timestampable):
    timestamp = models.DateTimeField(
        blank=False,
        null=False,
        verbose_name=_("timestamp"),
        help_text=_("Timestamp of the score"),
    )
    value = models.FloatField(
        blank=False,
        null=False,
        verbose_name=_("value"),
        help_text=_("Value of the score"),
    )
    playing_field = models.ForeignKey(
        "parladata.Organization",
        on_delete=models.CASCADE,
        verbose_name=_("playing field"),
        help_text=_("Organization associated with the score"),
    )
    # TODO maybe add mandate?

    class Meta:
        abstract = True


class PersonScore(Score):
    person = models.ForeignKey(
        "parladata.Person",
        related_name="%(class)s_related",
        on_delete=models.CASCADE,
        verbose_name=_("person"),
        help_text=_("Select the person associated with the score"),
    )

    def __str__(self):
        return f"{self.person.name}: {self.value}"

    class Meta:
        abstract = True


class GroupScore(Score):
    group = models.ForeignKey(
        "parladata.Organization",
        related_name="%(class)s_related",
        on_delete=models.CASCADE,
        verbose_name=_("group"),
        help_text=_("Select the group associated with the score"),
    )

    def __str__(self):
        return f"{self.group.name}: {self.value}"

    class Meta:
        abstract = True


class SessionScore(Score):
    session = models.ForeignKey(
        "parladata.Session",
        related_name="%(class)s_related",
        on_delete=models.CASCADE,
        verbose_name=_("session"),
        help_text=_("Select the session associated with the score"),
    )

    def __str__(self):
        return f"{self.session.name}: {self.value}"

    class Meta:
        abstract = True


class VotingDistance(PersonScore):
    target = models.ForeignKey(
        "parladata.Person",
        related_name="target_people",
        on_delete=models.CASCADE,
        verbose_name=_("target"),
        help_text=_("Select the target person for the voting distance"),
    )


class GroupVotingDistance(GroupScore):
    target = models.ForeignKey(
        "parladata.Person",
        related_name="target_organizations",
        on_delete=models.CASCADE,
        verbose_name=_("target"),
        help_text=_("Select the target person for the group voting distance"),
    )


class PersonAvgSpeechesPerSession(PersonScore):
    pass


class AgreementWithGroup(PersonScore):
    value = models.FloatField(
        blank=False,
        null=True,
        verbose_name=_("value"),
        help_text=_("Value of the agreement with the group"),
    )


class PersonNumberOfQuestions(PersonScore):
    pass


class PersonMonthlyVoteAttendance(PersonScore):
    no_mandate = models.FloatField(
        blank=False,
        null=False,
        verbose_name=_("no mandate"),
        help_text=_("Percentage person has no mandate"),
    )
    no_data = models.FloatField(
        blank=False,
        null=False,
        verbose_name=_("no data"),
        help_text=_("Percentage person has no data"),
    )


class GroupMonthlyVoteAttendance(GroupScore):
    no_mandate = models.FloatField(
        blank=False,
        null=False,
        verbose_name=_("no mandate"),
        help_text=_("Percentage group has no mandate"),
    )
    no_data = models.FloatField(
        blank=False,
        null=False,
        verbose_name=_("no data"),
        help_text=_("Percentage group has no data"),
    )


class GroupNumberOfQuestions(GroupScore):
    pass


class PersonVoteAttendance(PersonScore):
    pass


class GroupVoteAttendance(GroupScore):
    pass


class PersonStyleScore(PersonScore):
    style = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("style"),
        help_text=_("Style of the person"),
    )


class GroupStyleScore(GroupScore):
    style = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("style"),
        help_text=_("Style of the group"),
    )


class PersonNumberOfSpokenWords(PersonScore):
    pass


class PersonTfidf(PersonScore):
    token = models.TextField(
        blank=False, null=False, verbose_name=_("token"), help_text=_("TFIDF token")
    )


class GroupTfidf(GroupScore):
    token = models.TextField(
        blank=False, null=False, verbose_name=_("token"), help_text=_("TFIDF token")
    )


class SessionTfidf(SessionScore):
    token = models.TextField(
        blank=False, null=False, verbose_name=_("token"), help_text=_("TFIDF token")
    )


class SessionGroupAttendance(SessionScore):
    group = models.ForeignKey(
        "parladata.Organization",
        related_name="%(class)s_related",
        on_delete=models.CASCADE,
        verbose_name=_("group"),
        help_text=_("Select the group associated with the session attendance"),
    )


class GroupDiscord(GroupScore):
    pass


class Quote(Timestampable):
    """Model for quoted text from speeches."""

    speech = models.ForeignKey(
        "parladata.Speech",
        related_name="quotes",
        on_delete=models.CASCADE,
        verbose_name=_("speech"),
        help_text=_("Select the speech from which the quote is taken"),
    )

    quote_content = models.TextField(
        blank=True,
        null=True,
        help_text="text quoted in a speech",
        verbose_name=_("quote content"),
    )

    start_index = models.IntegerField(
        blank=True,
        null=True,
        help_text="index of first character of quote string",
        verbose_name=_("start index"),
    )

    end_index = models.IntegerField(
        blank=True,
        null=True,
        help_text="index of last character of quote string",
        verbose_name=_("end index"),
    )


class GroupUnity(Score):
    vote = models.ForeignKey(
        "parladata.Vote",
        related_name="organization_vote_unities",
        on_delete=models.CASCADE,
        verbose_name=_("vote"),
        help_text=_("Select the vote associated with the group unity"),
    )
    group = models.ForeignKey(
        "parladata.Organization",
        related_name="organization_vote_unities",
        on_delete=models.CASCADE,
        verbose_name=_("group"),
        help_text=_("Select the group associated with the group unity"),
    )
