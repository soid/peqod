# Generated by Django 3.2 on 2021-08-20 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('courses', '0002_auto_20210514_2039'), ('courses', '0003_catalogupdate'), ('courses', '0004_alter_catalogupdate_added_date'), ('courses', '0005_auto_20210804_1150'), ('courses', '0006_course_level'), ('courses', '0007_course_semester_id')]

    dependencies = [
        ('courses', '0001_initial_squashed_0007_alter_course_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('culpa_link', models.URLField(null=True)),
                ('culpa_reviews_count', models.PositiveSmallIntegerField(null=True)),
                ('culpa_nugget', models.CharField(max_length=1, null=True)),
                ('wikipedia_link', models.URLField(null=True)),
                ('culpa_reviews', models.JSONField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='course',
            name='instructor_culpa_link',
        ),
        migrations.RemoveField(
            model_name='course',
            name='instructor_culpa_reviews_count',
        ),
        migrations.RemoveField(
            model_name='course',
            name='instructor_wikipedia_link',
        ),
        migrations.AddField(
            model_name='course',
            name='edited_date',
            field=models.DateTimeField(auto_now=True, verbose_name='date edited'),
        ),
        migrations.AlterField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.instructor'),
        ),
        migrations.CreateModel(
            name='CatalogUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_date', models.DateField(verbose_name='date added')),
                ('typ', models.IntegerField(default=0)),
                ('diff', models.TextField(null=True)),
                ('related_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
                ('related_instructor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.instructor')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='semester_id',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
