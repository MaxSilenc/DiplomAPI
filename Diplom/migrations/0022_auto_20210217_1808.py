# Generated by Django 3.0.5 on 2021-02-17 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0021_projects_theme_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='projects',
            name='type',
            field=models.CharField(default=1, max_length=20),
        ),
    ]
