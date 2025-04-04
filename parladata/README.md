# parladata
parladata

# setup with croatian database
* docker-compose build
* docker-compose up -d
* docker-compose exec parladata python manage.py download_and_set_database

# setup with minimal setup
* docker-compose build
* docker-compose up -d
* docker-compose exec parladata python manage.py migrate
* docker-compose exec parladata python manage.py min_seed

user for login: parlauser:password

# using a backup to simulate production
* download backup file from backup place
* decrypt backup
* unzip backup
* run `docker-compose down -v` in bash to lose the database
* run `docker-compose up`, in bash the database should be accessible at port 5432
* connect to the database and execute `CREATE USER <user_name_from_backup> WITH PASSWORD '<some_password>';` then execute `GRANT ALL ON SCHEMA public TO <user_name_from_backup>;`
* restore database with psql `</path/to/>psql --file=</path/to/backup/file> --username=postgres --host=localhost --port=5432 parladata`

# Editing the test database

*   load fresh data with
    *   `import_db.sh` (import fresh MOL database) (use database dump from mol_test_db.zip if there's no mol database online)
        *   copy database
        *   load database
    *   edit command `parladata/management/commands/prepare_test_database.py` to create changes in data
    *   `python manage.py prepare_test_database` (delete unnecessary data)
    *   `python manage.py migrate parlacards zero` (delete parlacards data)
    *   `python manage.py migrate` (remigrate parlacards)
    *   `python manage.py run_all_analyses --start_time 2022-11-30` (run analyses at the end of 1st mandate)
    *   `python manage.py run_all_analyses --start_time 2022-12-13` (run analyses after session in 2nd mandate)
*   or
    *   `python manage.py flush` (flush your data (warning, irreversible deletion))
    *   `python manage.py loaddata tests/fixtures/test_db.json`
    *   Edit the database as you see fit
*   `python manage.py dumpdata -e contenttypes -e auth.permission -o tests/fixtures/test_db.json` (Save test dump data to the appropriate folder.)


## Special cases that should not be overwritten
- vote id 11094 contains only anonymous ballots
- vote id 11093 contains some anonymous ballots
- vote id 11092 contains no ballots at all
