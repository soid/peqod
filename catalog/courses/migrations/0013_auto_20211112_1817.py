# Generated by Django 3.2 on 2021-11-12 18:17

from django.db import migrations, models


def get_points_min_max(points: str) -> (float, float):
    p_min, p_max = None, None
    if points:
        if '-' in points:
            lf, rt = points.split('-', 1)
            p_min, p_max = float(lf), float(rt)
        else:
            p_min = float(points)
            p_max = p_min
    return p_min, p_max


def compute_points(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for c in Course.objects.all():
        p_min, p_max = get_points_min_max(c.points)
        c.points_min = p_min
        c.points_max = p_max
        c.save(update_fields=['points_min', 'points_max'])


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20211101_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='points_max',
            field=models.DecimalField(decimal_places=1, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='points_min',
            field=models.DecimalField(decimal_places=1, max_digits=3, null=True),
        ),
        migrations.RunPython(compute_points, reverse_code=migrations.RunPython.noop),
    ]