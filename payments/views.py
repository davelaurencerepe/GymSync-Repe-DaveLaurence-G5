from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PaymentForm
from .models import Payment

STAFF_ROLES = ("ADMIN", "STAFF")


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role not in STAFF_ROLES:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped


def can_edit(user, payment):
    # Admin can edit all; staff only the payments they recorded
    return user.role == "ADMIN" or payment.recorded_by_id == user.id


@staff_required
def payment_list(request):
    q = request.GET.get("q", "").strip()
    payments = Payment.objects.select_related("member", "plan", "recorded_by")
    if q:
        payments = payments.filter(
            Q(member__username__icontains=q)
            | Q(member__first_name__icontains=q)
            | Q(member__last_name__icontains=q)
        )
    payments = list(payments)
    for p in payments:
        p.editable = can_edit(request.user, p)
    return render(request, "payments/payment_list.html", {"payments": payments, "q": q})


@staff_required
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.recorded_by = request.user
        payment.save()
        messages.success(
            request,
            f"Payment recorded. Membership valid until {payment.period_end}.",
        )
        return redirect("payments:list")
    return render(request, "payments/payment_form.html",
                  {"form": form, "title": "Record Payment"})


@staff_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if not can_edit(request.user, payment):
        raise PermissionDenied
    form = PaymentForm(request.POST or None, instance=payment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment updated.")
        return redirect("payments:list")
    return render(request, "payments/payment_form.html",
                  {"form": form, "title": "Edit Payment"})


@staff_required
def payment_delete(request, pk):
    if request.user.role != "ADMIN":
        raise PermissionDenied
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted.")
        return redirect("payments:list")
    return render(request, "payments/payment_confirm_delete.html", {"payment": payment})


@login_required
def my_payments(request):
    payments = Payment.objects.filter(member=request.user).select_related("plan")
    expiry = payments.aggregate(latest=Max("period_end"))["latest"]
    is_active = bool(expiry and expiry >= timezone.localdate())
    return render(request, "payments/my_payments.html",
                  {"payments": payments, "expiry": expiry, "is_active": is_active})