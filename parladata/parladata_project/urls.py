import debug_toolbar
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from parlacards.admin_views import (
    RunMembersTFIDFView,
    RunOrganizationTFIDFView,
    RunSessionTFIDFView,
)
from parladata.views import (
    add_anonymous_ballots,
    add_ballots,
    merge_organizations,
    merge_people,
    merge_sessions,
)

urlpatterns = [
    # authentication
    path(
        "oauth/",
        include(("oauth2_provider.urls", "oauth"), namespace="oauth2_provider"),
    ),
    # admin views
    path("admin/parladata/parliamentmember/mergepeople/", merge_people),
    path("admin/parladata/parliamentarygroup/mergeorganizations/", merge_organizations),
    path("admin/parladata/session/mergesessions/", merge_sessions),
    path("admin/parladata/vote/addballots/", add_ballots),
    path("admin/parladata/vote/addanonymousballots/", add_anonymous_ballots),
    path(
        "run-members-tfidf/", RunMembersTFIDFView.as_view(), name="members_tfidf_task"
    ),
    path(
        "run-organizations-tfidf/",
        RunOrganizationTFIDFView.as_view(),
        name="orgranization_tfidf_task",
    ),
    path(
        "run-session-tfidf/<int:session>/",
        RunSessionTFIDFView.as_view(),
        name="session_tfidf_task",
    ),
    path("admin/", admin.site.urls),
    # REST api
    path("v3/", include(("parladata.urls", "apiV3"), namespace="APIv3")),
    path("v3/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # card data api
    path(
        "v3/cards/", include(("parlacards.urls", "parlacards"), namespace="parlacards")
    ),
    # card export api
    path("v3/export/", include("export.urls")),
    # notifications api
    path("v3/notifications/", include("parlanotifications.urls")),
    # Django debug toolbar
    path("__debug__/", include(debug_toolbar.urls)),
    # martor markdown editor
    path("martor/", include("martor.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
