# Generated by Django 4.2 on 2025-03-14 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelrequest_app', '0004_userprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admin',
            old_name='name',
            new_name='username',
        ),
        migrations.RemoveField(
            model_name='admin',
            name='email',
        ),
        migrations.AddField(
            model_name='admin',
            name='password',
            field=models.CharField(default='admin', max_length=150),
        ),
    ]
