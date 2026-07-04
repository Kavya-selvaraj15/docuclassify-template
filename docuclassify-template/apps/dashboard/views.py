from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from apps.documents.models import Document


@login_required
def home(request):
    """
    Simple RBAC-aware dashboard: admins/auditors see everything,
    everyone else sees only their own uploads.
    """
    if request.user.role in ("admin", "auditor") or request.user.is_superuser:
        documents = Document.objects.all()
    else:
        documents = Document.objects.filter(uploaded_by=request.user)

    category_breakdown = documents.values("category").annotate(count=Count("id")).order_by("-count")
    tier_breakdown = documents.values("classified_tier").annotate(count=Count("id")).order_by("-count")

    context = {
        "documents": documents[:20],
        "total_count": documents.count(),
        "category_breakdown": category_breakdown,
        "tier_breakdown": tier_breakdown,
    }
    return render(request, "dashboard/home.html", context)
