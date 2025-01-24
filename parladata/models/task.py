from datetime import datetime

from django.db import models

from parladata.behaviors.models import Taggable, Timestampable


class Task(Timestampable, Taggable):
    started_at = models.DateTimeField(
        help_text="time when started", blank=True, null=True, default=None
    )
    finished_at = models.DateTimeField(
        help_text="time when finished", blank=True, null=True, default=None
    )
    errored_at = models.DateTimeField(
        help_text="time when errored", blank=True, null=True, default=None
    )
    module_name = models.TextField(default="parladata.tasks", help_text="Name of task")
    name = models.TextField(blank=False, null=False, help_text="Name of task")
    email_msg = models.TextField(
        blank=False,
        null=False,
        help_text="A message sent to the administrator when the task is complete.",
    )
    payload = models.JSONField(help_text="Payload kwargs")
