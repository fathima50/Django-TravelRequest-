# Generated by Django 4.2 on 2025-03-12 09:40

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('travelrequest_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='travelrequest',
            old_name='travel_from_date',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='travelrequest',
            old_name='travel_to_date',
            new_name='start_date',
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='Admin_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='date_of_request',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='travelrequest',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='travelrequest_app.manager'),
        ),
        migrations.AlterField(
            model_name='travelrequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('closed', 'closed'), ('update request', 'update request')], default='Pending', max_length=20),
        ),
    ]
