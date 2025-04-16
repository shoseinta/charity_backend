from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from charity.models import Charity
from beneficiary.models import BeneficiaryUserRegistration

# Create your models here.



class BeneficiaryRequestTypeLayer1(models.Model):
    beneficiary_request_type_layer1_id = models.AutoField(primary_key=True)
    beneficiary_request_type_layer1_name = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('cash', 'Cash'), ('service', 'Service')],
        unique=True
    )
    beneficiary_request_type_layer1_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_type_layer1_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_beneficiary_request_type_layer1_name_display()

class BeneficiaryRequestTypeLayer2(models.Model):
    beneficiary_request_type_layer2_id = models.AutoField(primary_key=True)
    beneficiary_request_type_layer2_name = models.CharField(max_length=255, unique=True)
    beneficiary_request_type_layer2_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_type_layer2_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_request_type_layer1 = models.ForeignKey(BeneficiaryRequestTypeLayer1, on_delete=models.CASCADE)

    def __str__(self):
        return self.beneficiary_request_type_layer2_name

class BeneficiaryRequestDuration(models.Model):
    beneficiary_request_duration_id = models.AutoField(primary_key=True)
    beneficiary_request_duration_name = models.CharField(
        max_length=10,
        choices=[('one_time', 'One Time'), ('recurring', 'Recurring'), ('permanent', 'Permanent')],
        unique=True
    )
    beneficiary_request_duration_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_duration_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_beneficiary_request_duration_name_display()

class BeneficiaryRequestProcessingStage(models.Model):
    beneficiary_request_processing_stage_id = models.AutoField(primary_key=True)
    beneficiary_request_processing_stage_name = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('pending_review', 'Pending Review'),
            ('under_evaluation', 'Under Evaluation'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed')
        ],
    )
    beneficiary_request_status = models.CharField(
        max_length=8,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
    )
    beneficiary_request_processing_stage_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_processing_stage_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_beneficiary_request_processing_stage_name_display()} ({self.get_beneficiary_request_status_display()})"

class BeneficiaryRequest(models.Model):
    beneficiary_request_id = models.AutoField(primary_key=True)
    beneficiary_request_type_layer1 = models.ForeignKey(BeneficiaryRequestTypeLayer1, on_delete=models.PROTECT)
    beneficiary_request_type_layer2 = models.ForeignKey(BeneficiaryRequestTypeLayer2, on_delete=models.PROTECT)
    beneficiary_request_title = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_request_description = models.TextField(blank=True, null=True)
    beneficiary_request_duration = models.ForeignKey(
        BeneficiaryRequestDuration, 
        on_delete=models.PROTECT, 
        blank=True, 
        null=True,
        related_name='requests'
    )
    beneficiary_request_document = models.FileField(upload_to='request_docs/', blank=True, null=True)
    beneficiary_request_processing_stage = models.ForeignKey(BeneficiaryRequestProcessingStage, on_delete=models.CASCADE)
    beneficiary_request_date = models.DateField(blank=True, null=True)
    beneficiary_request_time = models.TimeField(blank=True, null=True)
    beneficiary_request_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_updated_at = models.DateTimeField(auto_now=True)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    beneficiary_user_registration = models.ForeignKey(BeneficiaryUserRegistration, on_delete=models.CASCADE, related_name='beneficiary_requests')

    def __str__(self):
        return f"Request #{self.beneficiary_request_id} - {self.beneficiary_request_title}"

class BeneficiaryRequestDurationOnetime(models.Model):
    beneficiary_request_duration_onetime_id = models.AutoField(primary_key=True)
    beneficiary_request_duration_onetime_deadline = models.DateField()
    beneficiary_request_duration_onetime_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_duration_onetime_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_request_duration = models.ForeignKey(BeneficiaryRequestDuration, on_delete=models.CASCADE)
    beneficiary_request = models.OneToOneField(BeneficiaryRequest, on_delete=models.CASCADE,related_name='beneficiary_request_duration_onetime')

    def __str__(self):
        return f"One-time deadline: {self.beneficiary_request_duration_onetime_deadline}"

class BeneficiaryRequestDurationRecurring(models.Model):
    beneficiary_request_duration_recurring_id = models.AutoField(primary_key=True)
    beneficiary_request_duration_recurring_limit = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    beneficiary_request_duration_recurring_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_duration_recurring_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_request_duration = models.ForeignKey(BeneficiaryRequestDuration, on_delete=models.CASCADE)
    beneficiary_request = models.OneToOneField(BeneficiaryRequest, on_delete=models.CASCADE,related_name='beneficiary_request_duration_recurring')

    def __str__(self):
        return f"Recurring limit: {self.beneficiary_request_duration_recurring_limit}"

class BeneficiaryRequestHistory(models.Model):
    beneficiary_request_history_id = models.AutoField(primary_key=True)
    beneficiary_request_history_title = models.CharField(max_length=255)
    beneficiary_request_history_description = models.TextField()
    beneficiary_request_history_document = models.FileField(upload_to='history_docs/', blank=True, null=True)
    beneficiary_request_history_date = models.DateField(blank=True, null=True)
    beneficiary_request_history_time = models.TimeField(blank=True, null=True)
    beneficiary_request_history_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_history_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_request = models.ForeignKey(BeneficiaryRequest, on_delete=models.CASCADE, related_name='beneficiary_request_history')

    def __str__(self):
        return f"History: {self.beneficiary_request_history_title}"

class BeneficiaryRequestChild(models.Model):
    beneficiary_request_child_id = models.AutoField(primary_key=True)
    beneficiary_request_child_description = models.TextField()
    beneficiary_request_child_document = models.FileField(upload_to='child_docs/', blank=True, null=True)
    beneficiary_request_child_processing_stage = models.ForeignKey(BeneficiaryRequestProcessingStage, on_delete=models.CASCADE)
    beneficiary_request_child_date = models.DateField(blank=True, null=True)
    beneficiary_request_child_time = models.TimeField(blank=True, null=True)
    beneficiary_request_child_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_request_child_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_request = models.ForeignKey(BeneficiaryRequest, on_delete=models.CASCADE,related_name='beneficiary_request_child')

    def __str__(self):
        return f"Child request of #{self.beneficiary_request.beneficiary_request_id}"

class CharityWorkfield(models.Model):
    charity_workfield_id = models.AutoField(primary_key=True)
    charity_workfield_title = models.CharField(max_length=255)
    charity_workfield_description = models.TextField(blank=True, null=True)
    charity_workfield_created_at = models.DateTimeField(auto_now_add=True)
    charity_workfield_updated_at = models.DateTimeField(auto_now=True)
    charity = models.ForeignKey(Charity, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.charity_workfield_title
    

class CharityAnnouncementForRequest(models.Model):
    charity_announcement_for_request_id = models.AutoField(primary_key=True)
    charity_announcement_for_request_title = models.CharField(max_length=255)
    charity_announcement_for_request_description = models.TextField(blank=True, null=True)
    charity_announcement_for_request_created_at = models.DateTimeField(auto_now_add=True)
    charity_announcement_for_request_updated_at = models.DateTimeField(auto_now=True)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    beneficiary_request = models.ForeignKey(BeneficiaryRequest, on_delete=models.CASCADE)

    def __str__(self):
        return self.charity_announcement_for_request_title
