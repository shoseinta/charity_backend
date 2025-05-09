# Generated by Django 5.2 on 2025-05-01 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0011_alter_beneficiaryrequest_beneficiary_request_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiaryrequest',
            name='effective_date',
            field=models.DateTimeField(blank=True, db_index=True, help_text='Coalesce of beneficiary_request_date and beneficiary_request_created_at', null=True),
        ),
    ]
