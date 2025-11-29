from django.contrib import admin
from .models import (
    BloodRequest, Donation, DonationResponse, DonorAvailability,
    DonorRanking, HospitalBenefit, DonorVoucher
)

admin.site.register(BloodRequest)
admin.site.register(Donation)
admin.site.register(DonationResponse)
admin.site.register(DonorAvailability)
admin.site.register(DonorRanking)
admin.site.register(HospitalBenefit)
admin.site.register(DonorVoucher)
# Register your models here.
