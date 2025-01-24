from datetime import datetime
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from parladata.models.task import Task
from parladata.update_utils import send_email


class Command(BaseCommand):
    help = "Run "

    def handle(self, *args, **options):
        tasks = Task.objects.filter(started_at__isnull=True).order_by("created_at")
        msgs = []
        for task in tasks:
            try:
                # skip task if it's started in another runner
                check_task = Task.objects.get(id=task.id)
                if check_task.started_at:
                    continue
                tasks_module = import_module(task.module_name)
                task_method = getattr(tasks_module, task.name)
                task.started_at = datetime.now()
                task.save()
                task_method(**task.payload)
                task.finished_at = datetime.now()
                task.save()
                if task.email_msg:
                    msgs.append(task.email_msg)
            except Exception as e:
                self.stdout.write(str(e))
                task.errored_at = datetime.now()
                task.save()

        if msgs:
            editor_permission_group = Group.objects.filter(
                name__icontains="editor"
            ).first()
            for editor in editor_permission_group.user_set.all():
                send_email(
                    _("Completed tasks at the Parlameter ") + settings.INSTALATION_NAME,
                    editor.email,
                    "email_on_tasks_compeleted.html",
                    {
                        "base_url": settings.BASE_URL,
                        "msgs": msgs,
                        "instalation_name": settings.INSTALATION_NAME,
                    },
                )
