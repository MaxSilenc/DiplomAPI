# Generated by Django 3.0.5 on 2020-12-26 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0016_projects_headline_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='headline_name',
            field=models.CharField(max_length=30),
        ),
    ]
