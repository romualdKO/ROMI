from django.contrib import admin
from .models import BloodRequest, Donation , DonationResponse,DonorAvailability

admin.site.register(BloodRequest)
admin.site.register(Donation)
admin.site.register(DonationResponse)
admin.site.register(DonorAvailability)
# Register your models here.
