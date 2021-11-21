
## Database

### Connect to MySQL from host

    mysql -h localhost -P 3306 --protocol=tcp -u root -ppassword2 cu-graph-db

### Import Catalog

    python catalog/manage.py update_instructors
    python catalog/manage.py update_catalog 2021-Summer

In Docker contrainer you need to mount first catalog to
`/columbia-catalog-data`

### Create admin user

    DJANGO_SUPERUSER_PASSWORD=123 python catalog/manage.py createsuperuser --user root --email soid@dicefield.com --no-input

### Database migration

    python catalog/manage.py makemigrations
    python catalog/manage.py migrate

Squash migrations:

    python catalog/manage.py squashmigrations courses 0005 0011

Reverse migration:

    python catalog/manage.py migrate courses 0012

# Logo Author

[Shutterstock](https://www.shutterstock.com/image-illustration/ink-black-white-illustration-old-ship-755181730)
