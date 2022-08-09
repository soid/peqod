
# Setup

You need Docker for starting a development server.
Run docker-compose.yml

URL for the dev server: http://localhost:8000/

Then proceed to setting up and importing the database.
In Docker contrainer you need to mount catalog data to
`/columbia-catalog-data`. 

Then import the catalog:

    python catalog/manage.py migrate
    python catalog/manage.py update_instructors
    python catalog/manage.py update_catalog ALL

Create Django admin user:

    DJANGO_SUPERUSER_PASSWORD=123 python catalog/manage.py createsuperuser --user root --email soid@dicefield.com --no-input

You may want to stop memcached server for avoiding caching in development.

## Database

### Database migration

Create a migration after changing model:

    python catalog/manage.py makemigrations
    python catalog/manage.py migrate

Squash migrations:

    python catalog/manage.py squashmigrations courses 0005 0011

Reverse migration:

    python catalog/manage.py migrate courses 0012

### Import Catalog

    python catalog/manage.py update_instructors
    python catalog/manage.py update_catalog 2021-Summer

Or import all semester files:

    python catalog/manage.py update_catalog ALL


### Connect to MySQL from host

    mysql -h localhost -P 3306 --protocol=tcp -u root -ppassword2 cu-graph-db

# Logo Author

[Shutterstock](https://www.shutterstock.com/image-illustration/ink-black-white-illustration-old-ship-755181730)
