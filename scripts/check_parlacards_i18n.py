import glob
import itertools
import sys
import os
from collections import Counter
from pathlib import Path

from get_yaml_keys import get_yaml_keys

###########################################################################
# Output to file with `python check_parlacards_i18n.py > i18n_report.txt` #
###########################################################################


def box_print(text, box="#"):
    print(box * (len(text) + 4))
    print(f"{box} {text} {box}")
    print(box * (len(text) + 4))


def underline_print(text, underline="-"):
    print(text)
    print(underline * len(text))


def count_files(locales):
    counts = Counter()
    for locale in locales:
        counts[locale] = len(
            glob.glob(f"parlacards/cards/_i18n/{locale}/**/*", recursive=True)
        )
    return counts


def report_missing_files(locales):
    locale_paths = {}
    for locale in locales:
        locale_paths[locale] = [
            path.split(f"{locale}/")[-1]
            for path in glob.glob(
                f"parlacards/cards/_i18n/{locale}/**/*.yaml", recursive=True
            )
        ]

    all_files = set(itertools.chain(*locale_paths.values()))

    ret = False

    for locale in locales:
        this_locale_paths = set(locale_paths[locale])
        if this_locale_paths != all_files:
            box_print(locale, "+")
            missing_files = all_files - this_locale_paths
            for missing_file in missing_files:
                print(missing_file)
            print()
            ret = True

    return ret


def report_missing_keys(locales):
    file_paths_in_locale = {}
    all_keys_by_file = {}

    for locale in locales:
        # gather all files in a locale
        file_paths_in_locale[locale] = [
            path.split(f"{locale}/")[-1]
            for path in glob.glob(
                f"parlacards/cards/_i18n/{locale}/**/*.yaml", recursive=True
            )
        ]

        # gather all the keys
        for locale_file_path in file_paths_in_locale[locale]:
            if locale_file_path not in all_keys_by_file.keys():
                all_keys_by_file[locale_file_path] = set(
                    get_yaml_keys(f"parlacards/cards/_i18n/{locale}/{locale_file_path}")
                )
            else:
                all_keys_by_file[locale_file_path].update(
                    get_yaml_keys(f"parlacards/cards/_i18n/{locale}/{locale_file_path}")
                )

    ret = False
    missing_keys_count = Counter()

    for locale in locales:
        box_printed = False
        for locale_file_path in file_paths_in_locale[locale]:
            locale_keys = get_yaml_keys(
                f"parlacards/cards/_i18n/{locale}/{locale_file_path}"
            )
            if set(locale_keys) != all_keys_by_file[locale_file_path]:
                # print the locale title box only once on first occurrence
                if not box_printed:
                    box_print(locale, "+")
                    box_printed = True

                underline_print(locale_file_path, "-")

                for key in all_keys_by_file[locale_file_path] - set(locale_keys):
                    print(key)
                    missing_keys_count[locale_file_path] += 1
                print()

                ret = True

    if ret:
        print("Total missing keys:")
        for file_path, count in missing_keys_count.items():
            print(f"{file_path}: {count} missing keys")

    return ret


if __name__ == "__main__":
    dir_path = Path(__file__).parent.parent.resolve()
    os.chdir(dir_path)

    LOCALES = [path.split("/")[-1] for path in glob.glob("parlacards/cards/_i18n/*")]
    LOCALES.remove("d3locales.js")

    exit_with_error_code = False

    box_print("MISSING FILES REPORT")
    exit_with_error_code |= report_missing_files(LOCALES)

    print()

    box_print("MISSING KEYS REPORT")
    exit_with_error_code |= report_missing_keys(LOCALES)

    sys.exit(int(exit_with_error_code))
