
## Database

### Connect to MySQL from host

    mysql -h localhost -P 3306 --protocol=tcp -u root -ppassword2 cu-graph-db

### Import Catalog

    python catalog/manage.py update_catalog 2021-Summer

### Create admin user

    python catalog/manage.py createsuperuser --user root --email soid@dicefield.com --no-inp

