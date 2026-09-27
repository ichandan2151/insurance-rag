"""Forms for document upload and querying."""
from django import forms


class DocumentUploadForm(forms.Form):
    title = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Homeowners Policy HO-3",
        }),
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".pdf",
        }),
        help_text="Upload a PDF insurance policy document (max 50 MB).",
    )

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are supported.")
        if f.size > 50 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 50 MB.")
        return f


class QueryForm(forms.Form):
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Ask a question about your insurance policies...",
        }),
    )
