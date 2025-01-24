import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Download croatian database"

    def handle(self, *args, **options):
        self.stdout.write("\n")

        cro_dump_url = "https://data.10.parlametar.hr/data_static/parladata.pgsql"
        self.download(cro_dump_url, "/tmp")

        dump_path = "/tmp/parladata.pgsql"

        db = settings.DATABASES["default"]["NAME"]
        host = settings.DATABASES["default"]["HOST"]
        user = settings.DATABASES["default"]["USER"]
        password = settings.DATABASES["default"]["PASSWORD"]
        os.system(
            f"PGPASSWORD={password} psql -h {host} -U {user} -d {db} -f {dump_path} "
        )

    def download(self, url: str, dest_folder: str):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)  # create folder if it does not exist

        filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
        file_path = os.path.join(dest_folder, filename)

        r = requests.get(url, stream=True)
        if r.ok:
            print("saving to", os.path.abspath(file_path))
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))
