# Generated by Django 3.0.5 on 2020-12-25 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0006_auto_20201225_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='img',
            field=models.ImageField(default='main/static/img/project.png', upload_to=''),
        ),
    ]
