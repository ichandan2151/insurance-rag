"""JSON API views for the React frontend."""
import json
from functools import wraps

from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import PolicyDocument, AuditLog
from . import rag_client


def api_login_required(view_func):
    """Like @login_required but returns 401 JSON instead of redirecting."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


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


def _serialize_document(doc):
    return {
        "id": doc.id,
        "title": doc.title,
        "filename": doc.filename,
        "status": doc.status,
        "page_count": doc.page_count,
        "chunk_count": doc.chunk_count,
        "uploaded_by": doc.uploaded_by.username if doc.uploaded_by else None,
        "uploaded_at": doc.uploaded_at.isoformat(),
        "rag_document_id": doc.rag_document_id,
        "error_message": doc.error_message,
    }


def _serialize_audit(log):
    return {
        "id": log.id,
        "user": log.user.username if log.user else None,
        "action": log.action,
        "action_display": log.get_action_display(),
        "detail": log.detail,
        "ip_address": log.ip_address,
        "timestamp": log.timestamp.isoformat(),
        "query_text": log.query_text,
        "answer_text": log.answer_text,
        "response_model": log.response_model,
        "source_count": log.source_count,
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def api_login(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = authenticate(request, username=body.get("username", ""), password=body.get("password", ""))
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    login(request, user)
    _log(request, "login", f"User logged in: {user.username}")
    return JsonResponse({"user": {"id": user.id, "username": user.username}})


@csrf_exempt
@require_POST
@api_login_required
def api_logout(request):
    logout(request)
    return JsonResponse({"ok": True})


@require_GET
@api_login_required
def api_me(request):
    return JsonResponse({"user": {"id": request.user.id, "username": request.user.username}})


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

@require_GET
@api_login_required
def api_document_list(request):
    docs = PolicyDocument.objects.select_related("uploaded_by").all()
    return JsonResponse({"documents": [_serialize_document(d) for d in docs]})


@require_GET
@api_login_required
def api_document_detail(request, pk):
    try:
        doc = PolicyDocument.objects.select_related("uploaded_by").get(pk=pk)
    except PolicyDocument.DoesNotExist:
        return JsonResponse({"error": "Document not found"}, status=404)

    logs = AuditLog.objects.filter(detail__icontains=doc.filename).select_related("user")[:20]
    return JsonResponse({
        "document": _serialize_document(doc),
        "logs": [_serialize_audit(log) for log in logs],
    })


@csrf_exempt
@require_POST
@api_login_required
def api_document_upload(request):
    title = request.POST.get("title", "").strip()
    uploaded_file = request.FILES.get("file")

    if not title:
        return JsonResponse({"error": "Title is required"}, status=400)
    if not uploaded_file:
        return JsonResponse({"error": "File is required"}, status=400)

    doc = PolicyDocument.objects.create(
        title=title,
        filename=uploaded_file.name,
        file=uploaded_file,
        uploaded_by=request.user,
        status="processing",
    )
    _log(request, "upload", f"Uploaded: {uploaded_file.name}")

    try:
        result = rag_client.ingest_document(doc.file, title)
        doc.status = "indexed"
        doc.rag_document_id = result.get("document_id")
        doc.page_count = result.get("pages")
        doc.chunk_count = result.get("chunks")
        doc.save()
        _log(request, "ingest", f"Indexed: {title} ({doc.chunk_count} chunks)")
        return JsonResponse(_serialize_document(doc), status=201)
    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        doc.save()
        _log(request, "ingest", f"Failed: {title} — {e}")
        return JsonResponse({"error": f"Ingestion failed: {e}"}, status=502)


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
@api_login_required
def api_query(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    question = body.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "Question is required"}, status=400)

    top_k = body.get("top_k", 8)

    try:
        result = rag_client.query(question, top_k=int(top_k))
        _log(
            request, "query",
            detail=f"Q: {question[:200]}",
            query_text=question,
            answer_text=result.get("answer", ""),
            response_model=result.get("model", ""),
            source_count=len(result.get("sources", [])),
        )
        return JsonResponse(result)
    except Exception as e:
        _log(request, "query", f"Failed: {question[:200]} — {e}")
        return JsonResponse({"error": f"Query failed: {e}"}, status=502)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

@require_GET
@api_login_required
def api_audit(request):
    logs = AuditLog.objects.select_related("user").all()[:100]
    return JsonResponse({"logs": [_serialize_audit(log) for log in logs]})


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

@require_GET
@api_login_required
def api_stats(request):
    try:
        rag_client.health_check()
        rag_status = "online"
    except Exception:
        rag_status = "offline"

    return JsonResponse({
        "total_documents": PolicyDocument.objects.count(),
        "indexed": PolicyDocument.objects.filter(status="indexed").count(),
        "pending": PolicyDocument.objects.filter(status__in=["pending", "processing"]).count(),
        "failed": PolicyDocument.objects.filter(status="failed").count(),
        "rag_status": rag_status,
    })
