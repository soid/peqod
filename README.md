# Setup

You need Docker for starting a development server.

Run docker-compose:

```bash
docker-compose up -d
```

URL for the dev server: http://localhost:8000/

Then proceed to setting up and importing the database. In the Docker container you need to mount catalog data to `/columbia-catalog-data` (see `volumes` in `docker-compose.yml`):

```yaml
volumes:
  - /path/to/columbia-catalog-data:/columbia-catalog-data
```

For running `catalog/manage.py` commands, you should open `bash` inside docker container:
```bash
docker exec -it peqod-web /bin/bash
```

Then import the catalog:

```bash
python catalog/manage.py migrate
python catalog/manage.py update_instructors
python catalog/manage.py update_catalog ALL
```

If you want to import catalog only for one semester, specify it as the last argument:
```bash
python catalog/manage.py update_catalog 2026-Fall
```

Create Django admin user:

```bash
DJANGO_SUPERUSER_PASSWORD=123 python catalog/manage.py createsuperuser --user root --email soid@dicefield.com --no-input
```

You may want to stop the memcached server to avoid caching in development.

## Database

### Database migration

Create a migration after changing a model:

```bash
python catalog/manage.py makemigrations
python catalog/manage.py migrate
```

Squash migrations:

```bash
python catalog/manage.py squashmigrations courses 0005 0011
```

Reverse migration:

```bash
python catalog/manage.py migrate courses 0012
```

### Import Catalog

```bash
python catalog/manage.py update_instructors
python catalog/manage.py update_catalog 2021-Summer
```

Or import all semester files:

```bash
python catalog/manage.py update_catalog ALL
```

### Connect to MySQL from host

```bash
mysql -h localhost -P 3306 --protocol=tcp -u root -ppassword2 cu-graph-db
```

# Logo Author

[Shutterstock](https://www.shutterstock.com/image-illustration/ink-black-white-illustration-old-ship-755181730)
