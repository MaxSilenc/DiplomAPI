# Generated by Django 3.0.5 on 2021-01-30 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Diplom', '0017_auto_20201226_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=30)),
                ('project_id', models.CharField(max_length=20)),
                ('text', models.TextField()),
            ],
        ),
    ]