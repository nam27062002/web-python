# Generated by Django 4.2 on 2023-05-11 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_chat'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='lastlogin',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
