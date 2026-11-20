from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Payment

User = get_user_model()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["member", "plan", "amount", "method",
                  "payment_date", "period_start", "notes"]
        widgets = {
            "payment_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "period_start": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = User.objects.filter(role=User.Role.MEMBER)
        self.fields["member"].label_from_instance = (
            lambda u: f"{u.get_full_name() or u.username} ({u.username})"
        )

    def clean_payment_date(self):
        date = self.cleaned_data["payment_date"]
        if date > timezone.localdate():
            raise forms.ValidationError("Payment date cannot be in the future.")
        return date

    def clean(self):
        cleaned = super().clean()
        plan = cleaned.get("plan")
        amount = cleaned.get("amount")
        if plan and amount is not None and amount < plan.price:
            self.add_error(
                "amount",
                f"Amount is less than the {plan.name} plan price (₱{plan.price}).",
            )
        return cleaned