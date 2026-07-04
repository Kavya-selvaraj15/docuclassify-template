from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "uploaded_by", "category", "confidence", "classified_tier", "uploaded_at")
    list_filter = ("category", "classified_tier")
