# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from charity.models import Charity
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo)
from request.models import CharityWorkfield
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

class CharityRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        charity = Charity(
            charity_user_id=user,
            charity_username=validated_data['username'],
            charity_password=validated_data['password'],
        )
        charity.save()
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class CharityLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            charity_user = Charity.objects.filter(charity_username=username, charity_password=password)
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            if not charity_user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data
    

class BeneficiaryRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')  # Add charity_id to fields

    def validate_username(self, value):
        """
        Validate that username:
        1. Must be all numeric
        2. Must have length of exactly 10 digits
        """
        if not value.isdigit():
            raise serializers.ValidationError("Identification number must be all digits")
        
        if len(value) != 10:
            raise serializers.ValidationError("Length of identification number must be 10 digits")
            
        return value

    def validate(self, attrs):
        if BeneficiaryUserRegistration.objects.filter(identification_number=attrs['username']).exists():
            raise serializers.ValidationError({"username": "This beneficiary already exists"})
        if BeneficiaryUserRegistration.objects.filter(beneficiary_id = attrs['password']).exists():
            raise serializers.ValidationError({"beneficiary id": "this beneficiary id already exists"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        
        beneficiary = BeneficiaryUserRegistration.objects.create(
            benficiary_user_id=user,
            identification_number=validated_data['username'],
            beneficiary_id=validated_data['password'],
            password=validated_data['password'],  # Assign the selected charity
            # Add other required fields with default values if needed
        )
        beneficiary.save()
        
        
        return user
    
class BeneficiaryLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            beneficiary_user = BeneficiaryUserRegistration.objects.filter(identification_number=username, password=password)
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            if not beneficiary_user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data

class BeneficiaryUserRegistrationInfoSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            RegexValidator(
                regex='^09\d{9}$',
                message="Phone number must be 11 digits starting with '09'"
            )
        ]
    )
    
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    class Meta:
        model = BeneficiaryUserRegistration
        fields = ['phone_number', 'email']

    def validate_phone_number(self, value):
        """Validate phone number if provided"""
        if value:  # Only validate if phone number exists
            value = value.strip()
            if BeneficiaryUserRegistration.objects.exclude(pk=self.instance.pk).filter(phone_number=value).exists():
                raise serializers.ValidationError("This phone number is already registered")
        return value

    def validate_email(self, value):
        """Validate email if provided"""
        if value:  # Only validate if email exists
            value = value.strip()
            if BeneficiaryUserRegistration.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("This email is already registered")
        return value

    def validate(self, data):
        """Ensure at least one contact method is provided"""
        if not data.get('phone_number') and not data.get('email'):
            raise serializers.ValidationError("Either phone number or email must be provided")
        return data

class BeneficiaryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = '__all__'

    def validate_first_name(self, value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value
    def validate_last_name(self, value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value

class BeneficiaryInformationSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        exclude = ['beneficiary_user_registration']
        read_only_fields = ['beneficiary_user_information_id']

    def validate_first_name(self, value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value
    def validate_last_name(self, value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value
    
class CharityUsernameUpdate(serializers.ModelSerializer):
    class Meta:
        model = Charity
        fields = ['charity_username']
    
    def validate_charity_username(self, value):
        if Charity.objects.filter(charity_username=value).exists():
            raise serializers.ValidationError("This charity username is already taken.")
        return value


class CharityPasswordUpdateSerializer(serializers.ModelSerializer):
    charity_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = Charity
        fields = ['charity_password']
    
class BeneficiaryPasswordUpdate(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = BeneficiaryUserRegistration
        fields = ['password']

class BeneficiaryAddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        exclude = ['beneficiary_user_registration']
    def validate(self, data):
        city = data.get('city')
        province = data.get('province')
        if city != province:
            raise serializers.ValidationError("City must match the province")
        return data
    def validate_postal_code(self, value):
        if not value:
            return value
        if len(value) != 10:
            raise serializers.ValidationError("Postal code must be 10 digits")
        if not value.isdigit():
            raise serializers.ValidationError("Postal code must be numeric")
    def validate_longitude(self, value):
        if not value:
            return value
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        return value
    def validate_latitude(self, value):
        if not value:
            return value
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        return value

class BeneficiaryAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        exclude = ['beneficiary_user_registration']

class CharityWorkFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityWorkfield
        exclude = ['charity']
    
    def validate_charity_work_field_name(self, value):
        if CharityWorkfield.objects.filter(charity_work_field_name=value).exists():
            raise serializers.ValidationError("This charity work field name is already taken.")
        return value

    