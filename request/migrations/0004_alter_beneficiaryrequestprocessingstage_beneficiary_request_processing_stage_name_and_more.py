# Generated by Django 5.2 on 2025-04-16 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request', '0003_alter_beneficiaryrequest_beneficiary_request_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiaryrequestprocessingstage',
            name='beneficiary_request_processing_stage_name',
            field=models.CharField(choices=[('submitted', 'Submitted'), ('pending_review', 'Pending Review'), ('under_evaluation', 'Under Evaluation'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('in_progress', 'In Progress'), ('completed', 'Completed')], max_length=20),
        ),
        migrations.AlterField(
            model_name='beneficiaryrequestprocessingstage',
            name='beneficiary_request_status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=8),
        ),
    ]
