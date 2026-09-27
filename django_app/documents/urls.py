"""URL configuration for the documents app."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_document, name="upload"),
    path("query/", views.query_view, name="query"),
    path("documents/", views.document_list, name="document_list"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
    path("audit/", views.audit_log_view, name="audit_log"),
]
