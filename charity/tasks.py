# request/tasks.py
from celery import shared_task
from request.models import (CharityAnnouncementForRequest, 
                     BeneficiaryRequest,
                     )
from django.core.exceptions import ObjectDoesNotExist
from beneficiary.models import CharityAnnouncementToBeneficiary

def to_persian_numbers(number):
    """Convert English numbers to Persian numbers"""
    persian_numbers = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹'
    }
    num_str = str(number)
    return ''.join(persian_numbers[digit] for digit in num_str)

@shared_task(bind=True)
def create_request_announcement(self, request_id):
    """
    Async task to create an announcement for a newly created request
    """
    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        
        # Create the announcement with RTL Persian text
        announcement = CharityAnnouncementForRequest.objects.create(
            charity_announcement_for_request_title="درخواست ایجاد شد",
            charity_announcement_for_request_description=f"درخواست به شماره {persian_id} توسط خیریه برای شما ایجاد شد",
            beneficiary_request=request
        )
        
    except:
        pass
    

@shared_task
def update_request_announcement(request_id):
    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="درخواست بروزرسانی شد",
            charity_announcement_for_request_description=f"درخواست شما به شماره {persian_id} توسط خیریه بروزرسانی شد"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def delete_request_announcement(request_id):
    try:
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementToBeneficiary.objects.create(
            charity_announcement_for_request_title="حذف درخواست",
            charity_announcement_for_request_description=f"درخواست شما به شماره {persian_id} توسط خیریه حذف گردید"
        )
    except:
        pass

@shared_task
def create_child_request_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="ایجاد درخواست جزئی",
            charity_announcement_for_request_description=f"برای درخواست شما به شماره {persian_id} توسط خیریه یک درخواست جزئی ایجاد گردید"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی درخواست جزئی",
            charity_announcement_for_request_description=f"درخواست جزئی مربوط به درخواست شما به شماره {persian_id} توسط خیریه بروزرسانی شد"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest
    persian_id = to_persian_numbers(request_id)
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف درخواست جزئی",
        charity_announcement_for_request_description=f"درخواست جزئی مربوط به درخواست شما به شماره {persian_id} توسط خیریه حذف گردید"
    )

@shared_task
def create_recurring_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی بازه دریافت کمک",
            charity_announcement_for_request_description=f"بازه زمانی دریافت کمک مربوط به درخواست شما به شماره {persian_id} توسط خیریه بروزرسانی شد"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_recurring_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest
    persian_id = to_persian_numbers(request_id)
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف بازه زمانی دریافت کمک",
        charity_announcement_for_request_description=f"بازه زمانی دریافت کمک مربوط به درخواست شما به شماره {persian_id} توسط خیریه حذف گردید"
    )

@shared_task
def create_onetime_update_announcement(request_id):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروزرسانی بازه دریافت کمک",
            charity_announcement_for_request_description=f"بازه زمانی دریافت کمک مربوط به درخواست شما به شماره {persian_id} توسط خیریه بروزرسانی شد"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_onetime_deletion_announcement(request_id):
    from request.models import CharityAnnouncementForRequest
    persian_id = to_persian_numbers(request_id)
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="حذف بازه زمانی دریافت کمک",
        charity_announcement_for_request_description=f"بازه زمانی دریافت کمک مربوط به درخواست شما به شماره {persian_id} توسط خیریه حذف گردید"
    )

@shared_task
def create_stage_change_announcement(request_id, new_stage_name):
    from request.models import BeneficiaryRequest, CharityAnnouncementForRequest

    try:
        request = BeneficiaryRequest.objects.get(pk=request_id)
        persian_id = to_persian_numbers(request_id)
        readable_stage = new_stage_name.replace("_", " ").title()
        if readable_stage == 'Submitted':
            readable_stage = 'ارسال شده'
        elif readable_stage == 'Pending Review':
            readable_stage = 'در انتظار بررسی'
        elif readable_stage == 'Under Evaluation':
            readable_stage = 'در حال ارزیابی'
        elif readable_stage == 'Approved':
            readable_stage = 'تایید شده'
        elif readable_stage == 'Rejected':
            readable_stage = 'رد شده'
        elif readable_stage == 'In Progress':
            readable_stage = 'در حال انجام'
        elif readable_stage == 'Completed':
            readable_stage = 'تکمیل شده'
        CharityAnnouncementForRequest.objects.create(
            beneficiary_request=request,
            charity_announcement_for_request_title="بروز رسانی وضعیت درخواست",
            charity_announcement_for_request_description=f"وضعیت درخواست شما به شماره {persian_id} توسط خیریه به «{readable_stage}» تغییر پیدا کرد"
        )
    except BeneficiaryRequest.DoesNotExist:
        pass

@shared_task
def create_child_stage_change_announcement(request_id, new_stage_name):
    from request.models import CharityAnnouncementForRequest
    persian_id = to_persian_numbers(request_id)
    readable_stage = new_stage_name.replace("_", " ").title()
    if readable_stage == 'Submitted':
        readable_stage = 'ارسال شده'
    elif readable_stage == 'Pending Review':
        readable_stage = 'در انتظار بررسی'
    elif readable_stage == 'Under Evaluation':
        readable_stage = 'در حال ارزیابی'
    elif readable_stage == 'Approved':
        readable_stage = 'تایید شده'
    elif readable_stage == 'Rejected':
        readable_stage = 'رد شده'
    elif readable_stage == 'In Progress':
        readable_stage = 'در حال انجام'
    elif readable_stage == 'Completed':
        readable_stage = 'تکمیل شده'
    CharityAnnouncementForRequest.objects.create(
        beneficiary_request_id=request_id,
        charity_announcement_for_request_title="بروزرسانی وضعیت درخواست جزئی",
        charity_announcement_for_request_description=f"وضعیت درخواست جزئی مربوط به درخواست شما به شماره {persian_id} توسط خیریه به «{readable_stage}» تغییر پیدا کرد"
    )