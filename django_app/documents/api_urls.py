"""URL routing for JSON API endpoints."""
from django.urls import path
from . import api

urlpatterns = [
    path("login/", api.api_login, name="api_login"),
    path("logout/", api.api_logout, name="api_logout"),
    path("me/", api.api_me, name="api_me"),
    path("documents/", api.api_document_list, name="api_document_list"),
    path("documents/upload/", api.api_document_upload, name="api_document_upload"),
    path("documents/<int:pk>/", api.api_document_detail, name="api_document_detail"),
    path("query/", api.api_query, name="api_query"),
    path("audit/", api.api_audit, name="api_audit"),
    path("stats/", api.api_stats, name="api_stats"),
]
