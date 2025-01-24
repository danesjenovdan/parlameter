from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.translation import gettext as _

from parladata.models.public_question import PublicPersonQuestion
from parladata.update_utils import send_email


class Command(BaseCommand):
    help = "Send public questions emails"

    def handle(self, *args, **options):
        now = datetime.now()
        previous_parse = now - timedelta(hours=1)
        new_public_questions = PublicPersonQuestion.objects.filter(
            created_at__gte=previous_parse
        )  # new public questions
        editor_permission_group = Group.objects.filter(name__icontains="editor").first()

        if new_public_questions:
            for editor in editor_permission_group.user_set.all():
                send_email(
                    _("New public questions for approval in parameter ")
                    + settings.INSTALATION_NAME,
                    editor.email,
                    "daily_notification.html",
                    {
                        "base_url": settings.BASE_URL,
                        "new_public_questions": new_public_questions,
                        "instalation_name": settings.INSTALATION_NAME,
                    },
                )

        questions = PublicPersonQuestion.objects.filter(
            notification_sent_at__isnull=True, approved_at__isnull=False
        ).exclude(rejected_at__isnull=False)
        for question in questions:
            email = question.recipient_person.email
            if email:
                translation.activate(settings.EMAIL_LANGUAGE_CODE)
                send_email(
                    f"#{question.id} " + _("Question from Parlameter"),
                    email,
                    "public_question_email.html",
                    {
                        "text": question.text,
                        "person_name": question.recipient_person.name,
                    },
                    reply_to=settings.REPLY_TO_EMAIL,
                )
                question.notification_sent_at = datetime.now()
                question.save()
