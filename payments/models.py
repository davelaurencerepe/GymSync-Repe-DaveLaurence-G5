from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class MembershipPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (₱{self.price})"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("gcash", "GCash"),
        ("card", "Card"),
        ("bank", "Bank Transfer"),
    ]

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments"
    )
    plan = models.ForeignKey(
        MembershipPlan, on_delete=models.PROTECT, related_name="payments"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default="cash")
    payment_date = models.DateField(default=timezone.localdate)
    period_start = models.DateField(default=timezone.localdate)
    period_end = models.DateField(editable=False)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-id"]

    def save(self, *args, **kwargs):
        self.period_end = self.period_start + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member} - ₱{self.amount} ({self.payment_date})"