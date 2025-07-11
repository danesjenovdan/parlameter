# -*- coding: utf-8 -*-
from .defaults import *

# generate your secret key with
# python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
env = dict(
    SECRET_KEY=os.getenv(
        "DJANGO_SECRET_KEY", "r^&^$8c*g$6db1s!s7uk9c!v%*ps)_0)h$!f3m7$%(o4b+5qwk"
    ),
    DEBUG=os.getenv("DJANGO_DEBUG", False),
    DATABASE_HOST=os.getenv("DJANGO_DATABASE_HOST", "localhost"),
    DATABASE_PORT=os.getenv("DJANGO_DATABASE_PORT", "5432"),
    DATABASE_NAME=os.getenv("DJANGO_DATABASE_NAME", "parladata"),
    DATABASE_USER=os.getenv("DJANGO_DATABASE_USERNAME", "postgres"),
    DATABASE_PASSWORD=os.getenv("DJANGO_DATABASE_PASSWORD", "postgres"),
    STATIC_ROOT=os.getenv("DJANGO_STATIC_ROOT", os.path.join(BASE_DIR, "../static")),
    STATIC_URL=os.getenv("DJANGO_STATIC_URL_BASE", "/static/"),
    MEDIA_ROOT=os.getenv("DJANGO_MEDIA_ROOT", os.path.join(BASE_DIR, "../media")),
    MEDIA_URL=os.getenv("DJANGO_MEDIA_URL_BASE", "/media/"),
    SOLR_URL=os.getenv("PARLAMETER_SOLR_URL", "http://solr:8983/solr/parlasearch"),
    ER_API_KEY=os.getenv("EVENTREGISTRY_API_KEY", ""),
    INSTALATION_NAME=os.getenv("INSTALATION_NAME", ""),
    PARSER_INTERVAL_HOURS=int(os.getenv("PARSER_INTERVAL_HOURS", 24)),
    DJANGO_BASE_URL=os.getenv("DJANGO_BASE_URL", "http://localhost:8000"),
)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env["SECRET_KEY"]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env["DEBUG"]

CSRF_TRUSTED_ORIGINS = [env["DJANGO_BASE_URL"]]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": env["DATABASE_HOST"],
        "PORT": env["DATABASE_PORT"],
        "NAME": env["DATABASE_NAME"],
        "USER": env["DATABASE_USER"],
        "PASSWORD": env["DATABASE_PASSWORD"],
    }
}

if os.getenv("PARLAMETER_ENABLE_MEMCACHED", False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
            "LOCATION": os.getenv("PARLAMETER_MEMCACHED_LOCATION", None),
            "TIMEOUT": None,
            "KEY_PREFIX": os.getenv("PARLAMETER_MEMCACHED_KEY_PREFIX", ""),
            "OPTIONS": {
                "binary": True,
                "username": os.getenv("PARLAMETER_MEMCACHED_USERNAME", ""),
                "password": os.getenv("PARLAMETER_MEMCACHED_PASSWORD", ""),
                "behaviors": {
                    "tcp_nodelay": True,
                },
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
            "TIMEOUT": None,
        }
    }
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

BASE_URL = env["DJANGO_BASE_URL"]

# static files for development
# STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "../static_files")]

STATIC_ROOT = env["STATIC_ROOT"]

# static files for production
STATIC_URL = env["STATIC_URL"]

MEDIA_ROOT = env["MEDIA_ROOT"]
MEDIA_URL = env["MEDIA_URL"]

SOLR_URL = env["SOLR_URL"]


# Mail settings

EMAIL_BACKEND = os.getenv(
    "PARLAMETER_EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend"
)
EMAIL_FILE_PATH = os.getenv("PARLAMETER_EMAIL_FILE_PATH", "/tmp/emails")
EMAIL_USE_TLS = bool(os.getenv("PARLAMETER_EMAIL_USE_TLS", ""))
EMAIL_USE_SSL = bool(os.getenv("PARLAMETER_EMAIL_USE_SSL", ""))
EMAIL_HOST = os.getenv("PARLAMETER_EMAIL_HOST", "dummy")
EMAIL_PORT = int(os.getenv("PARLAMETER_EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("PARLAMETER_SMTP_USER", "dummy")
EMAIL_HOST_PASSWORD = os.getenv("PARLAMETER_SMTP_PASSWORD", "dummy")
FROM_EMAIL = os.getenv("PARLAMETER_FROM_EMAIL", "info@parlameter.si")
REPLY_TO_EMAIL = os.getenv("PARLAMETER_REPLY_TO_EMAIL", "info@parlameter.si")

PARLAMETER_ENABLE_S3 = os.getenv("PARLAMETER_ENABLE_S3", False)
# DJANGO STORAGE SETTINGS
if PARLAMETER_ENABLE_S3:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.getenv("PARLAMETER_AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("PARLAMETER_AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.getenv("PARLAMETER_AWS_STORAGE_BUCKET_NAME", "")
    AWS_DEFAULT_ACL = (
        "public-read"  # if files are not public they won't show up for end users
    )
    AWS_QUERYSTRING_AUTH = (
        False  # query strings expire and don't play nice with the cache
    )
    AWS_LOCATION = os.getenv("PARLAMETER_AWS_LOCATION", "parladata")
    AWS_S3_REGION_NAME = os.getenv("PARLAMETER_AWS_REGION_NAME", "fr-par")
    AWS_S3_ENDPOINT_URL = os.getenv(
        "PARLAMETER_AWS_S3_ENDPOINT_URL", "https://s3.fr-par.scw.cloud"
    )
    AWS_S3_SIGNATURE_VERSION = os.getenv("PARLAMETER_AWS_S3_SIGNATURE_VERSION", "s3v4")
    AWS_S3_FILE_OVERWRITE = (
        False  # don't overwrite files if uploaded with same file name
    )

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}

LEMMATIZER_LANGUAGE_CODE = os.getenv("LEMMATIZER_LANGUAGE_CODE", "sl")

# TODO make separated env variable for LEGISLATION_RESOLVER_LANGUAGE_CODE or use generic env variable
LEGISLATION_RESOLVER_LANGUAGE_CODE = os.getenv("LEMMATIZER_LANGUAGE_CODE", "sl")
EMAIL_LANGUAGE_CODE = os.getenv("EMAIL_LANGUAGE_CODE", "sl")

if sentry_url := os.getenv("DJANGO_SENTRY_URL", False):
    # imports should only happen if necessary
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        sentry_url,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", 0.001)),
        send_default_pii=True,
    )

ER_API_KEY = env["ER_API_KEY"]

INSTALATION_NAME = env["INSTALATION_NAME"]
PARSER_INTERVAL_HOURS = env["PARSER_INTERVAL_HOURS"]

DRF_RECAPTCHA_DOMAIN = os.getenv("DRF_RECAPTCHA_DOMAIN", "www.google.com")
DRF_RECAPTCHA_SITE_KEY = os.getenv("DRF_RECAPTCHA_SITE_KEY", "")
DRF_RECAPTCHA_SECRET_KEY = os.getenv("DRF_RECAPTCHA_SECRET_KEY", "")

DRF_RECAPTCHA_TESTING = False
if not DRF_RECAPTCHA_SECRET_KEY or not DRF_RECAPTCHA_SITE_KEY:
    DRF_RECAPTCHA_TESTING = True

LANGUAGES = [
    ("bs", "Bosnian"),
    ("hr", "Croatian"),
    ("sl", "Slovenščina"),
    ("en", "English"),
]

LANGUAGE_CODE = os.getenv("PARLAMETER_LANGUAGE_CODE", "sl")

TIME_ZONE = "Europe/Ljubljana"

LOCALE_PATHS = [os.path.join(os.path.dirname(BASE_DIR), "locale/")]
