# -*- coding: utf-8 -*-
from defaults import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "hashhashhashhashashwkopaskfpjoij3rijfdsf2332fdw!!"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "localhost",
        "NAME": "parladata",
        "USER": "parlauser",
        "PASSWORD": "parlapassword",
    }
}

# static files for development
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# static files for production
STATIC_URL = "/parlastatic/parlalize/"
STATIC_ROOT = "/home/parlauser/parlastatic/parlalize/"


RAVEN_CONFIG = {
    #'dsn': 'http://123sdfsd123:123gdfsg123@sentry.url.si/40',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    #    'release': raven.fetch_git_sha(os.path.dirname(__file__)),
}


# Mail settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "host.si"
EMAIL_PORT = 587
EMAIL_HOST_USER = "user"
EMAIL_HOST_PASSWORD = "password"

ADMINS = [("admin", "admin@mail.com")]

DATA_ADMINS = [("data admin", "dataadmin@mail.com")]

PARSER_ADMINS = [("parser admin", "parseradmin@mail.com")]

PARLALIZE_API_KEY = "parlalize_api_key"
SETTER_KEY = "setter_api_key"

DASHBOARD_URL = "http://localhost:8881"

FORCE_SCRIPT_NAME = "/data"

# National Assembly id in database
DZ_ID = 95
PEOPLE_ID = None
COALITION_ID = 95
OPPOSITION_ID = 95

country = "SI"

PS = "pg"

PS_NP = ["pg", "unaligned MP"]

PS_NP_D = ["pg", "unaligned MP", "club"]
WBS = ["committee", "comission", "investigative comission"]

FRIENDSHIP_GROUP = ["friendship group"]

DELEGATION = ["delegation"]

COUNCIL = ["council"]

# ['ministrstvo', 'vlada']
MINISTRY_GOV = ["ministry", "gov"]

GOV_STAFF = ["gov_service", "gov_office"]
