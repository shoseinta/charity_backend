from rest_framework import serializers
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo,
                                CharityAnnouncementToBeneficiary,
                                Province,
                                City,)
from request.models import (BeneficiaryRequest,
                            BeneficiaryRequestHistory,
                            BeneficiaryRequestChild,
                            BeneficiaryRequestDurationOnetime,
                            BeneficiaryRequestDurationRecurring,
                            BeneficiaryRequestDuration,
                            CharityAnnouncementForRequest,)
import re

class BenefciaryProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['province_name']

class BeneficiaryCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city_name', 'province']

class BeneficiaryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = ["beneficiary_user_information_id",
                   "under_charity_support",
                   "first_name",
                   "last_name",
                   "gender",
                   "birth_date"]
        
class BeneficiaryAddressSerializer(serializers.ModelSerializer):
    province = BenefciaryProvinceSerializer()
    city = BeneficiaryCitySerializer()
    
    class Meta:
        model = BeneficiaryUserAddress
        fields = ["beneficiary_user_address_id",
                   "province",
                   "city"]

class BeneficiaryAdditionalInfo(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        fields = "__all__"

class BeneficiaryInformationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        exclude = ['beneficiary_user_registration']
    @staticmethod
    def validate_first_name(value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value
    @staticmethod
    def validate_last_name(value):
         # Regular expression to match Persian characters and common punctuation
        persian_regex = re.compile(r'^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200F\s]+$')
        
        if not persian_regex.match(value):
            raise serializers.ValidationError("This field must contain only Farsi (Persian) characters.")
        return value
        
class BeneficiaryAddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        exclude = ['beneficiary_user_registration']
    @staticmethod
    def validate(data):
        city = data.get('city')
        province = data.get('province')
        if city != province:
            raise serializers.ValidationError("City must match the province")
        return data
    @staticmethod
    def validate_postal_code(value):
        if not value:
            return value
        if len(value) != 10:
            raise serializers.ValidationError("Postal code must be 10 digits")
        if not value.isdigit():
            raise serializers.ValidationError("Postal code must be numeric")
    @staticmethod
    def validate_longitude(value):
        if not value:
            return value
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        return value
    @staticmethod
    def validate_latitude(value):
        if not value:
            return value
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        return value


class BeneficiaryAdditionalInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        exclude = ['beneficiary_user_registration']

class BeneficiaryAdditionalInfoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        fields = [
            'beneficiary_user_additional_info_title',
        ]



class BeneficiaryListSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()

    province_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()

    additional_info_list = serializers.SerializerMethodField()

    class Meta:
        model = BeneficiaryUserRegistration
        fields = [
            'beneficiary_user_registration_id',
            'identification_number',
            'beneficiary_id',
            'phone_number',
            'email',
            'first_name',
            'last_name',
            'gender',
            'birth_date',
            'province_name',
            'city_name',
            'additional_info_list',
        ]

    # --- Related fields manual access ---
    @staticmethod
    def get_first_name(obj):
        return getattr(obj.beneficiary_user_information, 'first_name', None)

    @staticmethod
    def get_last_name(obj):
        return getattr(obj.beneficiary_user_information, 'last_name', None)

    @staticmethod
    def get_gender(obj):
        return getattr(obj.beneficiary_user_information, 'gender', None)

    @staticmethod
    def get_birth_date(obj):
        return getattr(obj.beneficiary_user_information, 'birth_date', None)

    @staticmethod
    def get_province_name(obj):
        return getattr(getattr(obj.beneficiary_user_address, 'province', None), 'province_name', None)

    @staticmethod
    def get_city_name(obj):
        return getattr(getattr(obj.beneficiary_user_address, 'city', None), 'city_name', None)

    # --- Additional info optimized ---
    @staticmethod
    def get_additional_info_list(obj):
        additional_infos = getattr(obj, 'beneficiary_user_additional_info', None)
        if additional_infos is not None:
            return [info.beneficiary_user_additional_info_title for info in additional_infos.all()]
        return []



class RequestCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        exclude = ['beneficiary_user_registration']

    @staticmethod
    def validate(data):
        layer1 = data.get('beneficiary_request_type_layer1')
        layer2 = data.get('beneficiary_request_type_layer2')

        # Check if Layer 2 is associated with Layer 1
        if layer2.beneficiary_request_type_layer1 != layer1:
            raise serializers.ValidationError(
                "The selected request type Layer 2 is not associated with the selected request type Layer 1."
            )

        return data


class BeneficiaryInformationAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = '__all__'
        
class BeneficiaryAddressAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = '__all__'

class BeneficiaryRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestHistory
        fields = '__all__'

class BeneficiaryChildRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestChild
        fields = '__all__'

class BeneficiaryRequestOneTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        fields = '__all__'

class BeneficiaryRequestRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        fields = '__all__'

class BeneficiaryRequestUpdateOneTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        fields = ['beneficiary_request_duration_onetime_deadline']

class BeneficiaryRequestUpdateRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        fields = ['beneficiary_request_duration_recurring_limit']

class BeneficiaryRequestAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementForRequest
        fields = '__all__'

class BeneficiaryGetRequestSerializer(serializers.ModelSerializer):
    beneficiary_request_duration_onetime = BeneficiaryRequestOneTimeSerializer(read_only=True)
    beneficiary_request_duration_recurring = BeneficiaryRequestRecurringSerializer(read_only=True)  # Updated to read_only=True
    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'

class BeneficiaryRequestAnnouncementUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementForRequest
        exclude = ['beneficiary_request']
        
class BeneficiaryRequestChangeProcessingStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        fields = ['beneficiary_request_processing_stage']

class BeneficiaryUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        exclude = ['beneficiary_user_registration']
    @staticmethod
    def validate(data):
        layer1 = data.get('beneficiary_request_type_layer1')
        layer2 = data.get('beneficiary_request_type_layer2')

        # Check if Layer 2 is associated with Layer 1
        if layer2.beneficiary_request_type_layer1 != layer1:
            raise serializers.ValidationError(
                "The selected request type Layer 2 is not associated with the selected request type Layer 1."
            )

        return data
class BeneficiaryListSingleSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryInformationAllSerializer()
    beneficiary_user_address = BeneficiaryAddressAllSerializer()
    beneficiary_user_additional_info = BeneficiaryAdditionalInfo(many=True)
    #beneficiary_requests = BeneficiaryGetRequestSerializer(many=True)
    class Meta:
        model = BeneficiaryUserRegistration
        fields = '__all__'

class SingleRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestHistory
        exclude = ['beneficiary_request']

class SingleRequestChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestChild
        fields = '__all__'


class BeneficiarySingleRequestOneTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        exclude = ['beneficiary_request']
    @staticmethod
    def validate(data):
        if data['beneficiary_request_duration'] != BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='one_time'):
            raise serializers.ValidationError("This request must be a onetime request.")
        return data

class BeneficiarySingleRequestRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        exclude = ['beneficiary_request']

    @staticmethod
    def validate(data):
        if data['beneficiary_request_duration'] != BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='recurring'):
            raise serializers.ValidationError("This request must be a recurring request.")
        return data
    
class CharityAnnouncementToBeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityAnnouncementToBeneficiary
        exclude = ['beneficiary_user_registration']

class BeneficiaryRequestGetOnetimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        fields = '__all__'

class BeneficiaryRequestGetRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        fields = '__all__'