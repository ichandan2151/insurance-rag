"""Models for document management and audit logging."""
from django.db import models
from django.conf import settings


class PolicyDocument(models.Model):
    """Tracks insurance policy documents uploaded and indexed via the RAG service."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("indexed", "Indexed"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=500)
    filename = models.CharField(max_length=500)
    file = models.FileField(upload_to="policy_documents/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    page_count = models.IntegerField(null=True, blank=True)
    chunk_count = models.IntegerField(null=True, blank=True)
    rag_document_id = models.IntegerField(
        null=True, blank=True, help_text="Document ID in Flask RAG service"
    )
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class AuditLog(models.Model):
    """Audit trail for AI governance — logs all RAG interactions."""

    ACTION_CHOICES = [
        ("upload", "Document Upload"),
        ("ingest", "Document Ingested"),
        ("query", "Query Submitted"),
        ("eval", "Evaluation Run"),
        ("delete", "Document Deleted"),
        ("login", "User Login"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    detail = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # For query actions — store the question and response metadata
    query_text = models.TextField(blank=True, default="")
    response_model = models.CharField(max_length=100, blank=True, default="")
    source_count = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_action_display()} by {self.user}"
