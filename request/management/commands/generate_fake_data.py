import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from beneficiary.models import (
    BeneficiaryUserRegistration, BeneficiaryUserInformation, BeneficiaryUserAddress,
    Province, City
)
from request.models import (
    BeneficiaryRequest, BeneficiaryRequestDuration, BeneficiaryRequestDurationOnetime,
    BeneficiaryRequestDurationRecurring, BeneficiaryRequestTypeLayer1,
    BeneficiaryRequestTypeLayer2, BeneficiaryRequestProcessingStage
)

def random_or_none(generator):
    return generator() if random.choice([True, False]) else None

# --- Generate Beneficiaries ---
existing_beneficiary_count = BeneficiaryUserRegistration.objects.count()
if existing_beneficiary_count < 1003:
    provinces = list(Province.objects.all())
    cities = list(City.objects.all())

    for i in range(1000):
        user = User.objects.create_user(
            username=f"beneficiary_user_{existing_beneficiary_count + i + 1}",
            password="12345678"
        )

        reg = BeneficiaryUserRegistration.objects.create(
            benficiary_user_id=user,
            identification_number=f"{random.randint(1000000000, 9999999999)}",
            beneficiary_id=f"BNF{existing_beneficiary_count + i + 1:06d}",
            phone_number=random_or_none(lambda: f"09{random.randint(100000000, 999999999)}"),
            email=random_or_none(lambda: f"user{i}@example.com"),
            password="12345678"
        )

        BeneficiaryUserInformation.objects.create(
            beneficiary_user_registration=reg,
            under_charity_support=random.choice([True, False, None]),
            first_name=random_or_none(lambda: f"Name{i}"),
            last_name=random_or_none(lambda: f"Surname{i}"),
            gender=random.choice(['male', 'female', None]),
            birth_date=random_or_none(lambda: datetime.now().date() - timedelta(days=random.randint(18*365, 60*365)))
        )

        BeneficiaryUserAddress.objects.create(
            beneficiary_user_registration=reg,
            province=random.choice(provinces) if provinces else None,
            city=random.choice(cities) if cities else None,
            neighborhood=random_or_none(lambda: f"Neighborhood {i}"),
            street=random_or_none(lambda: f"Street {i}"),
            alley=random_or_none(lambda: f"Alley {i}"),
            building_number=random_or_none(lambda: random.randint(1, 200)),
            unit=random_or_none(lambda: random.randint(1, 20)),
            postal_code=random_or_none(lambda: f"{random.randint(10000,99999)}"),
            longitude=random_or_none(lambda: random.uniform(50.0, 60.0)),
            latitude=random_or_none(lambda: random.uniform(25.0, 40.0))
        )

# --- Generate Requests ---
existing_request_count = BeneficiaryRequest.objects.count()
if existing_request_count < 10003:
    beneficiaries = list(BeneficiaryUserRegistration.objects.all())
    durations = list(BeneficiaryRequestDuration.objects.all())
    stages = list(BeneficiaryRequestProcessingStage.objects.filter(beneficiary_request_processing_stage_id__in=range(3, 10)))
    layer1s = list(BeneficiaryRequestTypeLayer1.objects.all())
    layer2s = list(BeneficiaryRequestTypeLayer2.objects.all())

    for i in range(10000):
        beneficiary = random.choice(beneficiaries)
        layer1 = random.choice(layer1s)
        layer2 = random.choice([l2 for l2 in layer2s if l2.beneficiary_request_type_layer1 == layer1])
        duration = random.choice(durations)
        stage = random.choice(stages)

        request = BeneficiaryRequest.objects.create(
            beneficiary_user_registration=beneficiary,
            beneficiary_request_type_layer1=layer1,
            beneficiary_request_type_layer2=layer2,
            beneficiary_request_title=random_or_none(lambda: f"Request Title {i}"),
            beneficiary_request_description=random_or_none(lambda: f"Description of request {i}"),
            beneficiary_request_duration=duration,
            beneficiary_request_processing_stage=stage,
            beneficiary_request_date=random_or_none(lambda: timezone.now().date() - timedelta(days=random.randint(0, 1000))),
            beneficiary_request_time=random_or_none(lambda: (timezone.now() - timedelta(hours=random.randint(0, 24))).time()),
        )

        if duration.beneficiary_request_duration_name == "one_time":
            BeneficiaryRequestDurationOnetime.objects.create(
                beneficiary_request=request,
                beneficiary_request_duration=duration,
                beneficiary_request_duration_onetime_deadline=timezone.now().date() + timedelta(days=random.randint(30, 180))
            )

        elif duration.beneficiary_request_duration_name == "recurring":
            BeneficiaryRequestDurationRecurring.objects.create(
                beneficiary_request=request,
                beneficiary_request_duration=duration,
                beneficiary_request_duration_recurring_limit=random.randint(1, 12)
            )
