import uuid

from django.db import models

from parladata.behaviors.models import Timestampable


# Create your models here.
class NotificationUser(Timestampable):
    email = models.EmailField()
    hash = models.CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    latest_notification_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


class Keyword(Timestampable):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"

    class MatchingMethods(models.TextChoices):
        WIDE = "WIDE", "Wide"
        NARROW = "NARROW", "Narrow"

    keyword = models.CharField(max_length=255)
    user = models.ForeignKey(
        NotificationUser, related_name="keywords", on_delete=models.CASCADE
    )
    matching_method = models.CharField(
        max_length=10,
        choices=MatchingMethods.choices,
        default=MatchingMethods.WIDE,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    notification_frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        default=Frequency.DAILY,
    )
    latest_notification_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.keyword + " for " + self.user.email
