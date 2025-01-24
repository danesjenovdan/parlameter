from django.conf import settings

recaptcha_data = {
    "recaptcha": {
        "enabled": not settings.DRF_RECAPTCHA_TESTING,
        "domain": settings.DRF_RECAPTCHA_DOMAIN,
        "siteKey": settings.DRF_RECAPTCHA_SITE_KEY,
    }
}
