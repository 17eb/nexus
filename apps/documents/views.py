import uuid

from django.core import signing
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Document
from .serializers import (
    ConfirmUploadSerializer,
    DocumentSerializer,
    DocumentTypeSerializer,
    UploadRequestSerializer,
)


class PileDocumentsView(APIView):
    """GET /api/v1/piles/{pile_id}/documents/

    Unauthenticated for now — check_permission() doesn't exist until M2,
    same precedent as registry.PackagePilesView.
    """

    def get(self, request, pile_id):
        documents = list(services.get_documents_for_pile(pile_id))
        by_doc_type_id: dict[uuid.UUID, list[Document]] = {}
        for doc in documents:
            by_doc_type_id.setdefault(doc.doc_type_id, []).append(doc)

        sections = [
            {
                "doc_type": DocumentTypeSerializer(doc_type).data,
                "documents": DocumentSerializer(by_doc_type_id.get(doc_type.id, []), many=True).data,
            }
            for doc_type in services.list_document_types()
        ]
        return Response({"pile_id": str(pile_id), "sections": sections})


class RequestUploadView(APIView):
    """POST /api/v1/documents/upload-requests/

    body: {pile_id, doc_type_code, filename} -> {storage_key, upload_url}
    """

    def post(self, request):
        serializer = UploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.request_upload(**serializer.validated_data)
        return Response(result, status=201)


class ConfirmUploadView(APIView):
    """POST /api/v1/documents/

    body: {pile_id, doc_type_code, title, storage_key, content_type,
    supersedes?} -> Document. The other half of the upload flow: the
    client has already PUT the bytes to upload_url before calling this.
    """

    def post(self, request):
        serializer = ConfirmUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = services.confirm_upload(**serializer.validated_data)
        return Response(DocumentSerializer(document).data, status=201)


class DownloadView(APIView):
    """GET /api/v1/documents/{document_id}/download/

    302s to a presigned (or locally-faked) GET URL valid ~15 minutes —
    a plain <a href> works with or without JS on the frontend.
    """

    def get(self, request, document_id):
        return HttpResponseRedirect(services.build_download_url(document_id))


@method_decorator(csrf_exempt, name="dispatch")
class LocalStorageView(View):
    """Dev-only stand-in for a real presigned S3 URL — see
    documents.services._presign(). Not a "real" API endpoint: no DRF
    request/response machinery, just raw bytes in, raw bytes out.

    CSRF-exempt: the token itself (signed, single-purpose, expiring) is
    what authorizes this request, exactly like a real presigned S3 URL
    — there's no session to forge a request against, so Django's
    session-cookie-based CSRF protection doesn't apply here.
    """

    def put(self, request, token):
        try:
            storage_key = services._verify_local_storage_token(token, "upload")
        except signing.BadSignature:
            return HttpResponseBadRequest("Invalid or expired upload token.")
        default_storage.save(storage_key, ContentFile(request.body))
        return HttpResponse(status=204)

    def get(self, request, token):
        try:
            storage_key = services._verify_local_storage_token(token, "download")
        except signing.BadSignature:
            return HttpResponseBadRequest("Invalid or expired download token.")
        if not default_storage.exists(storage_key):
            return HttpResponseNotFound()
        return FileResponse(default_storage.open(storage_key, "rb"), as_attachment=True)
