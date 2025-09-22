from datetime import datetime

from django.db import models

from parladata.behaviors.models import Taggable, Timestampable


class Task(Timestampable, Taggable):
    started_at = models.DateTimeField(
        verbose_name="started_at",
        help_text="time when started",
        blank=True,
        null=True,
        default=None,
    )
    finished_at = models.DateTimeField(
        verbose_name="finished_at",
        help_text="time when finished",
        blank=True,
        null=True,
        default=None,
    )
    errored_at = models.DateTimeField(
        verbose_name="errored_at",
        help_text="time when errored",
        blank=True,
        null=True,
        default=None,
    )
    module_name = models.TextField(
        verbose_name="module_name",
        help_text="Name of task",
        default="parladata.tasks",
    )
    name = models.TextField(
        verbose_name="name",
        help_text="Name of task",
        blank=False,
        null=False,
    )
    email_msg = models.TextField(
        verbose_name="email_msg",
        help_text="A message sent to the administrator when the task is complete.",
        blank=False,
        null=False,
    )
    payload = models.JSONField(
        verbose_name="payload",
        help_text="Payload kwargs",
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
