# Generated by Django 3.2.23 on 2023-12-29 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chapter_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summary',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chapter_app.video'),
        ),
    ]
