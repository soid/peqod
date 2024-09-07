# Generated by Django 3.2.13 on 2024-09-07 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_course_courses_cou_locatio_be8f2c_idx'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['year', 'semester', 'semester_id'], name='courses_cou_year_2c4796_idx'),
        ),
    ]