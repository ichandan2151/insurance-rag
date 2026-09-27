"""Admin configuration for document management."""
from django.contrib import admin
from .models import PolicyDocument, AuditLog


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "filename", "status", "uploaded_by", "uploaded_at", "page_count", "chunk_count"]
    list_filter = ["status", "uploaded_at"]
    search_fields = ["title", "filename"]
    readonly_fields = ["rag_document_id", "page_count", "chunk_count", "error_message", "uploaded_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action", "detail_short", "ip_address"]
    list_filter = ["action", "timestamp"]
    search_fields = ["user__username", "detail", "query_text"]
    readonly_fields = [
        "user", "action", "detail", "ip_address", "timestamp",
        "query_text", "response_model", "source_count",
    ]

    def detail_short(self, obj):
        return obj.detail[:80] + "..." if len(obj.detail) > 80 else obj.detail
    detail_short.short_description = "Detail"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
