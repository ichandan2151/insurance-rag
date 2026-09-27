"""Views for document management, querying, and audit."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import PolicyDocument, AuditLog
from .forms import DocumentUploadForm, QueryForm
from . import rag_client


def _get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")


def _log(request, action, detail="", **kwargs):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        detail=detail,
        ip_address=_get_client_ip(request),
        **kwargs,
    )


@login_required
def dashboard(request):
    """Home page — document overview + quick query."""
    documents = PolicyDocument.objects.all()[:20]
    recent_logs = AuditLog.objects.all()[:10]
    stats = {
        "total_documents": PolicyDocument.objects.count(),
        "indexed": PolicyDocument.objects.filter(status="indexed").count(),
        "pending": PolicyDocument.objects.filter(status__in=["pending", "processing"]).count(),
        "failed": PolicyDocument.objects.filter(status="failed").count(),
    }

    # Check RAG service health
    try:
        rag_health = rag_client.health_check()
        rag_status = "online"
    except Exception:
        rag_status = "offline"

    return render(request, "documents/dashboard.html", {
        "documents": documents,
        "recent_logs": recent_logs,
        "stats": stats,
        "rag_status": rag_status,
    })


@login_required
def upload_document(request):
    """Upload and ingest a new policy document."""
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            title = form.cleaned_data["title"]

            doc = PolicyDocument.objects.create(
                title=title,
                filename=uploaded_file.name,
                file=uploaded_file,
                uploaded_by=request.user,
                status="processing",
            )
            _log(request, "upload", f"Uploaded: {uploaded_file.name}")

            # Send to Flask RAG service for ingestion
            try:
                result = rag_client.ingest_document(doc.file, title)
                doc.status = "indexed"
                doc.rag_document_id = result.get("document_id")
                doc.page_count = result.get("pages")
                doc.chunk_count = result.get("chunks")
                doc.save()
                _log(request, "ingest", f"Indexed: {title} ({doc.chunk_count} chunks)")
                messages.success(
                    request,
                    f"'{title}' uploaded and indexed — {doc.page_count} pages, {doc.chunk_count} chunks.",
                )
            except Exception as e:
                doc.status = "failed"
                doc.error_message = str(e)
                doc.save()
                _log(request, "ingest", f"Failed: {title} — {e}")
                messages.error(request, f"Ingestion failed: {e}")

            return redirect("dashboard")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload.html", {"form": form})


@login_required
def query_view(request):
    """Ask a question against indexed documents."""
    form = QueryForm()
    result = None

    if request.method == "POST":
        form = QueryForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]
            try:
                result = rag_client.query(question)
                _log(
                    request, "query",
                    detail=f"Q: {question[:200]}",
                    query_text=question,
                    response_model=result.get("model", ""),
                    source_count=len(result.get("sources", [])),
                )
            except Exception as e:
                messages.error(request, f"Query failed: {e}")
                _log(request, "query", f"Failed: {question[:200]} — {e}")

    return render(request, "documents/query.html", {
        "form": form,
        "result": result,
    })


@login_required
def document_list(request):
    """List all uploaded documents."""
    documents = PolicyDocument.objects.all()
    return render(request, "documents/document_list.html", {"documents": documents})


@login_required
def document_detail(request, pk):
    """Detail view for a single document."""
    doc = get_object_or_404(PolicyDocument, pk=pk)
    logs = AuditLog.objects.filter(detail__icontains=doc.filename)[:20]
    return render(request, "documents/document_detail.html", {"document": doc, "logs": logs})


@login_required
def audit_log_view(request):
    """View audit log — for governance."""
    logs = AuditLog.objects.all()[:100]
    return render(request, "documents/audit_log.html", {"logs": logs})
