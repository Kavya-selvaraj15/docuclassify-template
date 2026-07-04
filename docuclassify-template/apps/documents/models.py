from django.conf import settings
from django.db import models


class Document(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/")
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Classification results, filled in after pipeline runs
    category = models.CharField(max_length=50, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    classified_tier = models.CharField(max_length=20, blank=True, help_text="rules / ml / llm")

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_filename or self.file.name
