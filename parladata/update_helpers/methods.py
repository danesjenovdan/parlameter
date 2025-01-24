from django.conf import settings
from django.utils.module_loading import import_string


def get_helper_method(lib, name):
    language_code = settings.LEGISLATION_RESOLVER_LANGUAGE_CODE
    mathod_path_string = f"parladata.update_helpers.{language_code}.{lib}.{name}"
    try:
        method = import_string(mathod_path_string)
    except:
        print(f"method {name} for language code {language_code} are missing")
        print(f"check method {mathod_path_string}")
        method = lambda: None
    return method


def set_legislation_results():
    method = get_helper_method("legislation", "set_legislation_result")
    method()
