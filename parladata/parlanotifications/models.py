import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from parladata.behaviors.models import Timestampable


# Create your models here.
class NotificationUser(Timestampable):
    email = models.EmailField(
        verbose_name=_("email"),
        help_text=_("email"),
    )
    hash = models.CharField(
        verbose_name=_("hash"),
        help_text=_("Hash for email confirmation"),
        max_length=255,
    )
    uuid = models.UUIDField(
        verbose_name=_("uuid"),
        help_text=_("UUID for the user"),
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    latest_notification_sent_at = models.DateTimeField(
        verbose_name=_("latest notification sent at"),
        help_text=_("Date and time when the last notification was sent at"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("notification user")
        verbose_name_plural = _("notification users")

    def __str__(self):
        return self.email


class Keyword(Timestampable):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", _("Daily")
        WEEKLY = "WEEKLY", _("Weekly")
        MONTHLY = "MONTHLY", _("Monthly")

    class MatchingMethods(models.TextChoices):
        WIDE = "WIDE", _("Wide")
        NARROW = "NARROW", _("Narrow")

    keyword = models.CharField(
        verbose_name=_("keyword"),
        help_text=_("Notification keyword"),
        max_length=255,
    )
    user = models.ForeignKey(
        NotificationUser,
        verbose_name=_("user"),
        help_text=_("The user associated with this keyword"),
        related_name="keywords",
        on_delete=models.CASCADE,
    )
    matching_method = models.CharField(
        verbose_name=_("matching method"),
        help_text=_("The matching method for this keyword"),
        max_length=10,
        choices=MatchingMethods.choices,
        default=MatchingMethods.WIDE,
    )
    accepted_at = models.DateTimeField(
        verbose_name=_("accepted at"),
        help_text=_("Date and time when the user accepted the keyword"),
        null=True,
        blank=True,
    )
    notification_frequency = models.CharField(
        verbose_name=_("notification frequency"),
        help_text=_("The frequency of notifications for this keyword"),
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.DAILY,
    )
    latest_notification_sent_at = models.DateTimeField(
        verbose_name=_("latest notification sent at"),
        help_text=_("Date and time when the last notification was sent at"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("keyword")
        verbose_name_plural = _("keywords")

    def __str__(self):
        return self.keyword + " for " + self.user.email
