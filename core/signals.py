# core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.cache_manager import GlobalCacheManager

from beneficiary.models import (
    BeneficiaryUserRegistration,
    BeneficiaryUserAddress,
    BeneficiaryUserInformation,
    BeneficiaryUserAdditionalInfo,
)

from request.models import (
    BeneficiaryRequest,
    BeneficiaryRequestDurationOnetime,
    BeneficiaryRequestDurationRecurring,
    BeneficiaryRequestHistory,
    BeneficiaryRequestChild,
    CharityAnnouncementForRequest,
)

# --- Beneficiary Side Cache Invalidation ---

@receiver([post_save, post_delete], sender=BeneficiaryUserRegistration)
@receiver([post_save, post_delete], sender=BeneficiaryUserAddress)
@receiver([post_save, post_delete], sender=BeneficiaryUserInformation)
@receiver([post_save, post_delete], sender=BeneficiaryUserAdditionalInfo)
def invalidate_beneficiary_cache(sender, instance, **kwargs):
    try:
        beneficiary_id = instance.beneficiary_user_registration_id
    except AttributeError:
        beneficiary_id = instance.pk

    GlobalCacheManager.delete(GlobalCacheManager.make_key("beneficiary", "detail", beneficiary_id))
    GlobalCacheManager.delete(GlobalCacheManager.make_key("beneficiary", "list", "all"))

# --- Request Side Cache Invalidation ---

@receiver([post_save, post_delete], sender=BeneficiaryRequest)
@receiver([post_save, post_delete], sender=BeneficiaryRequestDurationOnetime)
@receiver([post_save, post_delete], sender=BeneficiaryRequestDurationRecurring)
@receiver([post_save, post_delete], sender=BeneficiaryRequestHistory)
@receiver([post_save, post_delete], sender=BeneficiaryRequestChild)
@receiver([post_save, post_delete], sender=CharityAnnouncementForRequest)
def invalidate_request_cache(sender, instance, **kwargs):
    try:
        request_id = instance.beneficiary_request_id
    except AttributeError:
        request_id = instance.pk

    GlobalCacheManager.delete(GlobalCacheManager.make_key("request", "detail", request_id))
    GlobalCacheManager.delete(GlobalCacheManager.make_key("request", "list", "all"))

# core/signals.py

from beneficiary.models import CharityAnnouncementToBeneficiary

@receiver([post_save, post_delete], sender=CharityAnnouncementToBeneficiary)
def invalidate_charity_announcement_cache(sender, instance, **kwargs):
    beneficiary_id = instance.beneficiary_user_registration_id
    GlobalCacheManager.delete(GlobalCacheManager.make_key("beneficiary", "announcement:list", beneficiary_id))
