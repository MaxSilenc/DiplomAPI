# Generated by Django 3.0.5 on 2020-12-25 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0011_remove_projects_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='project',
            field=models.FileField(default='default.txt', upload_to='Ue4Project'),
        ),
    ]
