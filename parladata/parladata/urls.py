from django.conf.urls import include
from django.urls import re_path, path
from rest_framework import routers

from parladata.api_views import *
from parladata.views import *

router = routers.DefaultRouter()
router.register(r"people", PersonView)
router.register(r"mandates", MandateView)
router.register(r"sessions", SessionView)
router.register(r"motions", MotionView)
router.register(r"links", LinkView)
router.register(r"documents", DocumentView)
router.register(r"ballots", BallotView)
router.register(r"votes", VoteView)
router.register(r"speeches", SpeechView)
router.register(r"organizations", OrganizationView)
# router.register(r'organization-names', OrganizationNameView)
router.register(r"legislation", LegislationView)
router.register(r"tags", TagsView)
router.register(r"person-memberships", PersonMembershipView)
router.register(r"areas", AreaView)
router.register(r"agenda-items", AgendaItemView)
router.register(r"questions", QuestionView)
router.register(r"answers", AnswerView)
router.register(r"organization-memberships", OrganizationMembershipsViewSet)
router.register(r"procedures", ProcedureViewSet)
router.register(r"procedure-phases", ProcedurePhaseViewSet)
router.register(r"legislation-consideration", LegislationConsiderationViewSet)
router.register(r"legislation-status", LegislationStatusViewSet)
router.register(r"legislation-classifications", LegislationClassificationViewSet)
router.register(r"media", MediumView)
router.register(r"media-reports", MediaReportView)
router.register(r"public-person-questions", PublicPersonQuestionView)
router.register(r"public-person-answers", PublicPersonAnswerView)

urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^merge-people", merge_people),
    re_path(r"^merge-organizations", merge_organizations),
    re_path(r"^add-ballots", add_ballots),
    path(
        r"end-memberships/<int:person_id>/",
        EndUserMembershipsView.as_view(),
        name="end-memberships",
    ),
]
