import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from src.leads.forms import CalculatorLeadForm, PhoneLeadForm, ReviewLeadForm
from src.leads.models import LeadSubmission
from src.leads.rate_limit import is_rate_limited
from src.leads.services import notify_calculator_lead, notify_phone_lead, notify_review_lead


def _client_key(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "unknown")
    return ip


@method_decorator(csrf_protect, name="dispatch")
class PhoneLeadView(View):
    def post(self, request):
        if is_rate_limited(_client_key(request)):
            return JsonResponse({"ok": False, "errors": {"__all__": ["Too many requests"]}}, status=429)
        form = PhoneLeadForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        data = form.cleaned_data
        LeadSubmission.objects.create(
            lead_type=LeadSubmission.LeadType.PHONE,
            phone=data["tel"],
            page_title=data.get("loc", ""),
            channel=data.get("channel", ""),
            payload=data,
        )
        notify_phone_lead(data["tel"], data.get("loc", ""), data.get("channel", ""))
        return JsonResponse({"ok": True})


@method_decorator(csrf_protect, name="dispatch")
class CalculatorLeadView(View):
    def post(self, request):
        if is_rate_limited(_client_key(request)):
            return JsonResponse({"ok": False, "errors": {"__all__": ["Too many requests"]}}, status=429)
        form = CalculatorLeadForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        data = form.cleaned_data
        LeadSubmission.objects.create(
            lead_type=LeadSubmission.LeadType.CALCULATOR,
            name=data["name"],
            phone=data["tel"],
            payload=data,
        )
        notify_calculator_lead(data)
        return JsonResponse({"ok": True})


@method_decorator(csrf_protect, name="dispatch")
class ReviewLeadView(View):
    def post(self, request):
        if is_rate_limited(_client_key(request)):
            return JsonResponse({"ok": False, "errors": {"__all__": ["Too many requests"]}}, status=429)
        form = ReviewLeadForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        data = form.cleaned_data
        LeadSubmission.objects.create(
            lead_type=LeadSubmission.LeadType.REVIEW,
            name=data["name"],
            payload=data,
        )
        notify_review_lead(data)
        return JsonResponse({"ok": True})
