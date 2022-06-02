# Generated by Django 4.0.4 on 2022-06-02 21:46

from django.db import migrations, models
import trails.models


class Migration(migrations.Migration):

    dependencies = [
        ('trails', '0011_trail_heightmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trail',
            name='heightmap',
            field=models.FileField(blank=True, null=True, upload_to=trails.models.heightmap_location),
        ),
    ]
