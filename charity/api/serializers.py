from rest_framework import serializers
from beneficiary.models import BeneficiaryUserRegistration,BeneficiaryUserInformation,BeneficiaryUserAddress,BeneficiaryUserAdditionalInfo
from request.models import (BeneficiaryRequest,
                            BeneficiaryRequestHistory,
                            BeneficiaryRequestChild,
                            BeneficiaryRequestDurationOnetime,
                            BeneficiaryRequestDurationRecurring,
                            BeneficiaryRequestDuration)

class BeneficiaryInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = ["beneficiary_user_information_id",
                   "under_charity_support",
                   "first_name",
                   "last_name",
                   "gender"]
        
class BeneficiaryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = ["beneficiary_user_address_id",
                   "province",
                   "city"]

class BeneficiaryAdditionalInfo(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAdditionalInfo
        fields = "__all__"

class BeneficiaryListSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryInformationSerializer()
    beneficiary_user_address = BeneficiaryAddressSerializer()
    beneficiary_user_additional_info = BeneficiaryAdditionalInfo(many=True)
    class Meta:
        model = BeneficiaryUserRegistration
        fields = ["beneficiary_user_registration_id",
                  "identification_number",
                  "beneficiary_id",
                  "phone_number",
                  "email",
                  "beneficiary_user_information",
                  "beneficiary_user_address",
                  "beneficiary_user_additional_info"
                  ]

class RequestCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'

    def validate(self, data):
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

class BeneficiaryGetRequestSerializer(serializers.ModelSerializer):
    beneficiary_request_history = BeneficiaryRequestHistorySerializer(many=True)
    beneficiary_request_child = BeneficiaryChildRequestSerializer(many=True)
    beneficiary_request_duration_onetime = BeneficiaryRequestOneTimeSerializer()
    beneficiary_request_duration_recurring = BeneficiaryRequestRecurringSerializer()
    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'

class BeneficiaryUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'
    def validate(self, data):
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
    beneficiary_requests = BeneficiaryGetRequestSerializer(many=True)
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
        exclude = ['beneficiary_request']


class BeneficiarySingleRequestOneTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationOnetime
        exclude = ['beneficiary_request']
    def validate(self,data):
        if data['beneficiary_request_duration'] != BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='one_time'):
            raise serializers.ValidationError("This request must be a onetime request.")
        return data

class BeneficiarySingleRequestRecurringSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequestDurationRecurring
        exclude = ['beneficiary_request']

    def validate(self,data):
        if data['beneficiary_request_duration'] != BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='recurring'):
            raise serializers.ValidationError("This request must be a recurring request.")
        return data