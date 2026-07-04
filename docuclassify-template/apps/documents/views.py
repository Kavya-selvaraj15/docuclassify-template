from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import DocumentUploadForm
from .models import Document
from .text_extraction import extract_text
from apps.classifier.pipeline import classify_document


@login_required
def upload_document(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.original_filename = request.FILES["file"].name
            doc.save()

            # Read the actual file content (PDF/image/spreadsheet) rather
            # than guessing from the filename.
            extracted_text = extract_text(request.FILES["file"])
            result = classify_document(extracted_text)

            doc.category = result["category"]
            doc.confidence = result["confidence"]
            doc.classified_tier = result["tier"]
            doc.save()

            return redirect("dashboard:home")
    else:
        form = DocumentUploadForm()
    return render(request, "documents/upload.html", {"form": form})
