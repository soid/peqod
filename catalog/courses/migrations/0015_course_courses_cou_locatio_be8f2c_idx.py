# Generated by Django 3.2.13 on 2023-09-26 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_auto_20211118_0718'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['location', 'year', 'semester'], name='courses_cou_locatio_be8f2c_idx'),
        ),
    ]
