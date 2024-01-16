# Generated by Django 3.2.23 on 2024-01-11 13:57

import chapter_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chapter_app', '0006_alter_video_video_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video_path',
            field=models.FileField(upload_to=chapter_app.models.Video.video_upload_path),
        ),
    ]
