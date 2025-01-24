import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ParladataConfig(AppConfig):
    name = "parladata"

    def ready(self):
        import parladata.signals
