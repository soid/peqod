# Generated by Django 3.2 on 2021-08-24 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_course_courses_cou_departm_9688c2_idx_squashed_0011_course_courses_cou_instruc_d2e347_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogupdate',
            name='semester',
            field=models.CharField(default='', max_length=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalogupdate',
            name='year',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
