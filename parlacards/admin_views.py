from datetime import datetime

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework.response import Response
from rest_framework.views import APIView

from parlacards.utils import get_playing_fields
from parladata.models.session import Session
from parladata.models.task import Task


class RunTask(APIView):
    task = None
    redirect_url_named = None

    def get(self, request, **kwargs):
        Task(
            name=self.task,
            payload={},
            module_name="parlacards.tasks",
            email_msg=self.message,
        ).save()
        return redirect(reverse(self.redirect_url_named))


class RunMembersTFIDFView(RunTask):
    message = _("Calculation of TFIDF for members is completed")
    task = "delay_members_tfidf_task"
    redirect_url_named = "admin:parladata_parliamentmember_changelist"


class RunOrganizationTFIDFView(RunTask):
    message = _("Calculation of TFIDF for organizations is completed")
    task = "delay_organization_tfidf_task"
    redirect_url_named = "admin:parladata_parliamentarygroup_changelist"


class RunSessionTFIDFView(APIView):
    def get(self, request, session):
        session_obj = get_object_or_404(Session, pk=session)
        message = (
            _("Calculation of TFIDF for session is completed: ") + session_obj.name
        )
        Task(
            name="delay_sessions_tfidf_task",
            payload={"pk": session},
            module_name="parlacards.tasks",
            email_msg=message,
        ).save()
        return redirect(reverse("admin:parladata_session_changelist"))
