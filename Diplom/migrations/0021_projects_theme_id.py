# Generated by Django 3.0.5 on 2021-02-16 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0020_theme'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='theme_id',
            field=models.CharField(default=1, max_length=20),
        ),
    ]
