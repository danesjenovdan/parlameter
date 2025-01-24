from __future__ import absolute_import, unicode_literals

"""
WSGI config for parladata project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# import arguments


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parladata_project.settings")
application = get_wsgi_application()
