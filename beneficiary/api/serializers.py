#a serializer for the Beneficiary model and models related to that
from rest_framework import serializers
from beneficiary.models import (
    BeneficiaryUserRegistration,
    BeneficiaryUserInformation,
    BeneficiaryUserAddress,
    CharityAnnouncementToBeneficiary,
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


class BeneficiaryUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserInformation
        fields = '__all__'

class BeneficiaryUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryUserAddress
        fields = '__all__'

class BeneficiaryUserSerializer(serializers.ModelSerializer):
    beneficiary_user_information = BeneficiaryUserInformationSerializer()
    beneficiary_user_address = BeneficiaryUserAddressSerializer()

    class Meta:
        model = BeneficiaryUserRegistration
        exclude = ['password']

class BeneficiaryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryRequest
        exclude = ['beneficiary_user_registration','beneficiary_request_processing_stage']
    
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
        exclude = ['beneficiary_request', 'beneficiary_request_child_processing_stage']

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

class BeneficiaryRequestGetSerializer(serializers.ModelSerializer):
    beneficiary_request_duration_onetime = BeneficiaryRequestOnetimeSerializer()
    beneficiary_request_duration_recurring = BeneficiaryRequestRecurringSerializer()
    beneficiary_request_history = BeneficiaryRequestHistorySerializer(many=True)
    beneficiary_request_child = BeneficiaryRequestChildSerializer(many=True, required=False)
    beneficiary_request_announcement = BeneficiaryRequestAnnouncementSerializer(many=True)

    class Meta:
        model = BeneficiaryRequest
        fields = '__all__'

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