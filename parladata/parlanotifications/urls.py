from django.conf.urls import include
from django.urls import re_path
from rest_framework import routers

from parlanotifications.views import KeywordView

router = routers.DefaultRouter()
router.register(r"keywords", KeywordView)


urlpatterns = [
    re_path(r"^", include(router.urls)),
]
