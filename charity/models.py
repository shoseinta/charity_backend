from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Charity(models.Model):
    charity_id = models.AutoField(primary_key=True)
    charity_user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    charity_name = models.CharField(max_length=255, blank=True, null=True)
    charity_username = models.CharField(max_length=255)
    charity_password = models.CharField(max_length=255)
    charity_phone_number = models.IntegerField(blank=True, null=True)
    charity_email = models.EmailField(blank=True, null=True)
    charity_created_at = models.DateTimeField(auto_now_add=True)
    charity_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.charity_name or self.charity_username
    
