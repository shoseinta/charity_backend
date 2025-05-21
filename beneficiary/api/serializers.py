#a serializer for the Beneficiary model and models related to that
from rest_framework import serializers
from beneficiary.models import (
    BeneficiaryUserRegistration,
    BeneficiaryUserInformation,
    BeneficiaryUserAddress,
    CharityAnnouncementToBeneficiary,
    BeneficiaryUserAdditionalInfo,
    Province,
    City,
)
from request.models import (
    BeneficiaryRequest,
    BeneficiaryRequestDurationOnetime,
    BeneficiaryRequestDurationRecurring,
    BeneficiaryRequestHistory,
    BeneficiaryRequestChild,
    BeneficiaryRequestDuration,
    CharityAnnouncementForRequest,
    BeneficiaryRequestTypeLayer1,
    BeneficiaryRequestTypeLayer2,
    BeneficiaryRequestProcessingStage,
)
import re


class BeneficiaryUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = '__all__'

class BeneficiaryUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = '__all__'

class BeneficiaryUserAdditionalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        fields = '__all__'

class BeneficiaryUserSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryUserInformationSerializer()
    beneficiary_user_address = BeneficiaryUserAddressSerializer()
    beneficiary_user_additional_info = serializers.SerializerMethodField()

    class Meta:
        model = BeneficiaryUserRegistration
        fields = '__all__'

    def get_beneficiary_user_additional_info(self, obj):
        additional_infos = obj.beneficiary_user_additional_info.filter(
            beneficiary_user_additional_info_is_created_by_charity=False
        )
        return BeneficiaryUserAdditionalInfoSerializer(additional_infos, many=True).data


class BeneficiaryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        exclude = ['beneficiary_user_registration','beneficiary_request_date','beneficiary_request_time','effective_date','beneficiary_request_processing_stage','beneficiary_request_is_created_by_charity']
    
    def validate(self, data):
        layer1 = data.get('beneficiary_request_type_layer1')
        layer2 = data.get('beneficiary_request_type_layer2')

        # Check if Layer 2 is associated with Layer 1
        if layer2 and layer2.beneficiary_request_type_layer1 != layer1:
            raise serializers.ValidationError(
                "The selected request type Layer 2 is not associated with the selected request type Layer 1."
            )

        return data
    
class BeneficiarySingleRequestOneTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        exclude = ['beneficiary_request', 'beneficiary_request_duration', 'beneficiary_request_duration_onetime_is_created_by_charity']

class BeneficiarySingleRequestRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        exclude = ['beneficiary_request', 'beneficiary_request_duration', 'beneficiary_request_duration_recurring_is_created_by_charity']

    
class BeneficiaryRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestHistory
        exclude = ['beneficiary_request']

class BeneficiaryRequestChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestChild
        exclude = ['beneficiary_request']

class BeneficiaryRequestChildCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestChild
        exclude = ['beneficiary_request','beneficiary_request_child_date','beneficiary_request_child_time', 'beneficiary_request_child_processing_stage','beneficiary_request_child_is_created_by_charity']

class BeneficiaryRequestChildGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestChild
        fields = '__all__'

class BeneficiaryRequestOnetimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        fields = '__all__'

class BeneficiaryRequestRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        fields = '__all__'

class BeneficiaryRequestAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementForRequest
        fields = '__all__'

from rest_framework import serializers

class BeneficiaryRequestGetSerializer(serializers.ModelSerializer):
    beneficiary_request_duration_onetime = BeneficiaryRequestOnetimeSerializer()
    beneficiary_request_duration_recurring = BeneficiaryRequestRecurringSerializer()
    beneficiary_request_history = BeneficiaryRequestHistorySerializer(many=True)
    beneficiary_request_child = BeneficiaryRequestChildSerializer(many=True, required=False)
    beneficiary_request_announcement = BeneficiaryRequestAnnouncementSerializer(many=True)

    beneficiary_request_type_layer1 = serializers.SerializerMethodField()
    beneficiary_request_type_layer2 = serializers.SerializerMethodField()
    beneficiary_request_duration = serializers.SerializerMethodField()
    beneficiary_request_processing_stage = serializers.SerializerMethodField()

    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'

    def get_beneficiary_request_type_layer1(self, obj):
        return obj.beneficiary_request_type_layer1.get_beneficiary_request_type_layer1_name_display()

    def get_beneficiary_request_type_layer2(self, obj):
        return obj.beneficiary_request_type_layer2.beneficiary_request_type_layer2_name

    def get_beneficiary_request_duration(self, obj):
        return obj.beneficiary_request_duration.get_beneficiary_request_duration_name_display() if obj.beneficiary_request_duration else None

    def get_beneficiary_request_processing_stage(self, obj):
        return obj.beneficiary_request_processing_stage.get_beneficiary_request_processing_stage_name_display()


class UpdateOnetimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        fields = ['beneficiary_request_duration_onetime_deadline']

class UpdateRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        fields = ['beneficiary_request_duration_recurring_limit']

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementToBeneficiary
        exclude = ['beneficiary_user_registration']

class BeneficiaryRequestTypeLayer1Serializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestTypeLayer1
        fields = '__all__'

class BeneficiaryRequestTypeLayer2Serializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestTypeLayer2
        fields = '__all__'

class BeneficiaryRequestProcessingStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestProcessingStage
        fields = '__all__'

class BeneficiaryRequestDurationLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDuration
        fields = '__all__'

class ProvinceLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'

class CityLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class RequestAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementForRequest
        fields = '__all__'

class BeneficiaryAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementToBeneficiary
        fields = '__all__'

class BeneficiaryInformationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        exclude = ['beneficiary_user_registration']
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

class BeneficiaryAddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        exclude = ['beneficiary_user_registration']
    def validate(self, data):
        city = data.get('city')
        province = data.get('province')
        try:
            city_obj = City.objects.get(pk=city.pk)  # Or use city.id
        except City.DoesNotExist:
            raise serializers.ValidationError("City does not exist.")

        if city_obj.province != province:
            raise serializers.ValidationError("Selected city does not belong to the selected province.")

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
    
class BeneficiaryAdditionalInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        exclude = ['beneficiary_user_registration','beneficiary_user_additional_info_is_created_by_charity']

class UpdatingDeletingBeneficiaryUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserRegistration
        exclude = ['identification_number','beneficiary_id','benficiary_user_id']
    
    def validate_phone_number(self, value):
        """Validate phone number: must be 11 digits, start with 09, and unique"""
        if value:
            value = value.strip()

            # Check Persian mobile format: 11 digits and starts with '09'
            if not re.fullmatch(r'09\d{9}', value):
                raise serializers.ValidationError("Phone number must be in Persian format: start with 09 and be 11 digits long.")

            # Uniqueness check excluding current instance (for updates)
            if BeneficiaryUserRegistration.objects.exclude(pk=getattr(self.instance, 'pk', None)).filter(phone_number=value).exists():
                raise serializers.ValidationError("This phone number is already registered.")

        return value

    def validate_email(self, value):
        """Validate email if provided"""
        if value:  # Only validate if email exists
            value = value.strip()
            if BeneficiaryUserRegistration.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("This email is already registered")
        return value
    
    