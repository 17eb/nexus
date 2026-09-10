from django.urls import path

from .views import (
    ConfirmUploadView,
    DownloadView,
    LocalStorageView,
    PileDocumentsView,
    RequestUploadView,
)

urlpatterns = [
    path("piles/<uuid:pile_id>/documents/", PileDocumentsView.as_view(), name="pile-documents"),
    path("documents/upload-requests/", RequestUploadView.as_view(), name="document-upload-request"),
    path("documents/", ConfirmUploadView.as_view(), name="document-confirm"),
    path(
        "documents/<uuid:document_id>/download/", DownloadView.as_view(), name="document-download"
    ),
    path(
        "documents/local-storage/<str:token>/",
        LocalStorageView.as_view(),
        name="document-local-storage",
    ),
]
