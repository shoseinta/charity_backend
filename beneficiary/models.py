from django.db import models
from charity.models import Charity
from django.contrib.auth.models import User

# Create your models here.
class Province(models.Model):
    province_name = models.CharField(max_length=255, unique=True, db_index=True)
    province_created_at = models.DateTimeField(auto_now_add=True)
    province_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.province_name

class City(models.Model):
    city_name = models.CharField(max_length=255, db_index=True)
    city_created_at = models.DateTimeField(auto_now_add=True)
    city_updated_at = models.DateTimeField(auto_now=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f"{self.city_name}, {self.province.province_name}"
    
class BeneficiaryUserRegistration(models.Model):
    beneficiary_user_registration_id = models.AutoField(primary_key=True)
    benficiary_user_id = models.OneToOneField(User, on_delete=models.CASCADE)  # username
    identification_number = models.CharField(max_length=10,unique=True,db_index=True)
    beneficiary_id = models.CharField(unique=True, max_length=10, db_index=True)  # username
    phone_number = models.CharField(unique=True, blank=True, null=True, max_length=11, db_index=True)
    email = models.EmailField(unique=True, blank=True, null=True, db_index=True)  # username
    password = models.CharField(max_length=255, blank=True, null=True)  # default: identification_number
    beneficiary_user_registration_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_user_registration_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.beneficiary_id}"


class BeneficiaryUserInformation(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    beneficiary_user_information_id = models.AutoField(primary_key=True)
    under_charity_support = models.BooleanField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True, null=True, db_index=True)
    birth_date = models.DateField(blank=True, null=True, db_index=True)
    beneficiary_user_information_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_user_information_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_user_registration = models.OneToOneField(BeneficiaryUserRegistration, on_delete=models.CASCADE, related_name="beneficiary_user_information")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BeneficiaryUserAddress(models.Model):
    beneficiary_user_address_id = models.AutoField(primary_key=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, blank=True, null=True, db_index=True, related_name='beneficiary_province')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, db_index=True, related_name='beneficiary_city')
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    alley = models.CharField(max_length=255, blank=True, null=True)
    building_number = models.PositiveIntegerField(blank=True, null=True)
    unit = models.PositiveIntegerField(blank=True, null=True)
    postal_code = models.CharField(blank=True, null=True, max_length=10, db_index=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    beneficiary_user_address_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_user_address_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_user_registration = models.OneToOneField(BeneficiaryUserRegistration, on_delete=models.CASCADE, related_name="beneficiary_user_address")

    def __str__(self):
        return f"{self.beneficiary_user_registration}"

class BeneficiaryUserAdditionalInfo(models.Model):
    beneficiary_user_additional_info_id = models.AutoField(primary_key=True)
    beneficiary_user_additional_info_title = models.CharField(max_length=255)
    beneficiary_user_additional_info_description = models.TextField(blank=True, null=True)
    beneficiary_user_additional_info_document = models.FileField(upload_to='beneficiary_docs/', blank=True, null=True)
    beneficiary_user_additional_info_is_created_by_charity = models.BooleanField(default=False)
    beneficiary_user_additional_info_created_at = models.DateTimeField(auto_now_add=True)
    beneficiary_user_additional_info_updated_at = models.DateTimeField(auto_now=True)
    beneficiary_user_registration = models.ForeignKey(BeneficiaryUserRegistration, on_delete=models.CASCADE, related_name="beneficiary_user_additional_info")

    def __str__(self):
        return self.beneficiary_user_additional_info_title
    
class CharityAnnouncementToBeneficiary(models.Model):
    charity_announcement_to_beneficiary_id = models.AutoField(primary_key=True)
    charity_announcement_to_beneficiary_title = models.CharField(max_length=255)
    charity_announcement_to_beneficiary_description = models.TextField(blank=True, null=True)
    charity_announcement_to_beneficiary_created_at = models.DateTimeField(auto_now_add=True)
    charity_announcement_to_beneficiary_updated_at = models.DateTimeField(auto_now=True)
    charity_announcement_to_beneficiary_seen = models.BooleanField(default=False)
    beneficiary_user_registration = models.ForeignKey(BeneficiaryUserRegistration, on_delete=models.CASCADE)

    def __str__(self):
        return self.charity_announcement_to_beneficiary_title