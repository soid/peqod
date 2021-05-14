
## Database

### Connect to MySQL from host

    mysql -h localhost -P 3306 --protocol=tcp -u root -ppassword2 cu-graph-db

### Import Catalog

    python catalog/manage.py update_catalog 2021-Summer
    python catalog/manage.py instructor_fields_mapping

### Create admin user

    DJANGO_SUPERUSER_PASSWORD=123 python catalog/manage.py createsuperuser --user root --email soid@dicefield.com --no-input

### Database migration

    python catalog/manage.py makemigrations
    python catalog/manage.py migrate
