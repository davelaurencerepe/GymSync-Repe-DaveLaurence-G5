from django.contrib import admin
from .models import MembershipPlan, Payment

admin.site.register(MembershipPlan)
admin.site.register(Payment)