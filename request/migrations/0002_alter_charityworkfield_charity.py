# Generated by Django 5.2 on 2025-04-15 14:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charity', '0001_initial'),
        ('request', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charityworkfield',
            name='charity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='charity.charity'),
        ),
    ]
