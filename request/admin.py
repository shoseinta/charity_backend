from django.contrib import admin
from .models import (
    BeneficiaryRequest,
    BeneficiaryRequestChild,
    BeneficiaryRequestDuration,
    BeneficiaryRequestDurationOnetime,
    BeneficiaryRequestDurationRecurring,
    BeneficiaryRequestHistory,
    BeneficiaryRequestProcessingStage,
    BeneficiaryRequestTypeLayer1,
    BeneficiaryRequestTypeLayer2,
)
# Register your models here.
admin.site.register(BeneficiaryRequest)
admin.site.register(BeneficiaryRequestChild)
admin.site.register(BeneficiaryRequestDuration)
admin.site.register(BeneficiaryRequestDurationOnetime)
admin.site.register(BeneficiaryRequestDurationRecurring)
admin.site.register(BeneficiaryRequestHistory)
admin.site.register(BeneficiaryRequestProcessingStage)
admin.site.register(BeneficiaryRequestTypeLayer1)
admin.site.register(BeneficiaryRequestTypeLayer2)