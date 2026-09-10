"""Public interface of the documents app. Only functions in this module
should be imported by other apps (enforced by the import-linter
contracts in pyproject.toml — apps.registry may not import
apps.documents.models directly)."""

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any

from django.core import signing
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from nexus.exceptions import DomainError

from apps.registry import services as registry_services

from .models import Document, DocumentType

__all__ = [
    "list_document_types",
    "get_documents_for_pile",
    "request_upload",
    "confirm_upload",
    "build_download_url",
    "get_pile_ids_with_documents",
    "UnknownDocumentTypeError",
    "UploadNotCompletedError",
]

logger = logging.getLogger(__name__)

LOCAL_STORAGE_SALT = "documents.local-storage"
PRESIGN_MAX_AGE = 60 * 15  # 15 minutes — docs/data-model.md's presigned-GET ceiling, reused for upload too.


class UnknownDocumentTypeError(DomainError):
    status_code = 400


class UploadNotCompletedError(DomainError):
    status_code = 409


def list_document_types() -> QuerySet[DocumentType]:
    return DocumentType.objects.order_by("sort_order")


def get_documents_for_pile(pile_id: uuid.UUID) -> QuerySet[Document]:
    """Current (non-superseded) documents only — see Document.supersedes."""
    registry_services.get_pile(pile_id)  # 404s on an unknown pile_id
    return (
        Document.objects.filter(pile_id=pile_id, superseded_by__isnull=True)
        .select_related("doc_type")
        .order_by("doc_type__sort_order", "-uploaded_at")
    )


def request_upload(*, pile_id: uuid.UUID, doc_type_code: str, filename: str) -> dict[str, str]:
    """Step 1 of the upload flow (docs/data-model.md): returns a
    storage_key and a URL the client PUTs the file bytes to directly.
    Creates no Document row — that happens at confirm_upload()."""
    registry_services.get_pile(pile_id)  # 404s if the pile doesn't exist
    doc_type = _get_document_type(doc_type_code)
    extension = Path(filename).suffix
    storage_key = f"documents/{pile_id}/{doc_type.code}/{uuid.uuid4().hex}{extension}"
    return {"storage_key": storage_key, "upload_url": _presign(storage_key, "upload")}


def confirm_upload(
    *,
    pile_id: uuid.UUID,
    doc_type_code: str,
    title: str,
    storage_key: str,
    content_type: str,
    supersedes: uuid.UUID | None = None,
) -> Document:
    """Step 2: the client has PUT the bytes to the URL from
    request_upload() and now confirms. checksum_sha256 and size_bytes
    are never trusted from the client — both are computed here by
    re-reading the object that's actually in storage."""
    pile = registry_services.get_pile(pile_id)
    doc_type = _get_document_type(doc_type_code)

    if not default_storage.exists(storage_key):
        raise UploadNotCompletedError(
            f"No object at storage_key={storage_key!r} — PUT the file to its upload_url before confirming."
        )
    checksum, size = _hash_and_size(storage_key)

    supersedes_obj = get_object_or_404(Document, pk=supersedes) if supersedes else None

    return Document.objects.create(
        pile=pile,
        doc_type=doc_type,
        title=title,
        storage_key=storage_key,
        checksum_sha256=checksum,
        size_bytes=size,
        content_type=content_type,
        supersedes=supersedes_obj,
    )


def build_download_url(document_id: uuid.UUID) -> str:
    document = get_object_or_404(Document, pk=document_id)
    # TODO(M3): replace this log line with a tracking.Event write
    # ("document.downloaded") once the append-only Event log exists —
    # docs/data-model.md's download flow calls for logging the access.
    logger.info(
        "document.downloaded id=%s pile_id=%s storage_key=%s",
        document.id,
        document.pile_id,
        document.storage_key,
    )
    return _presign(document.storage_key, "download")


def get_pile_ids_with_documents(pile_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    """For CorridorMap marker colour. Presence, not currency — a pile
    whose only document has since been superseded still counts, and in
    practice every pile with any upload history always has exactly one
    current (non-superseded) document, so filtering wouldn't change the
    result anyway."""
    return set(
        Document.objects.filter(pile_id__in=pile_ids).values_list("pile_id", flat=True).distinct()
    )


def _get_document_type(code: str) -> DocumentType:
    try:
        return DocumentType.objects.get(code=code)
    except DocumentType.DoesNotExist:
        raise UnknownDocumentTypeError(f"Unknown document type code: {code!r}") from None


def _hash_and_size(storage_key: str) -> tuple[str, int]:
    hasher = hashlib.sha256()
    size = 0
    with default_storage.open(storage_key, "rb") as f:
        for chunk in f.chunks():
            hasher.update(chunk)
            size += len(chunk)
    return hasher.hexdigest(), size


def _presign(storage_key: str, action: str) -> str:
    """The one place that knows the active storage backend. Today this
    always targets the local filesystem backend's stand-in views
    (LocalStorageView) via a signed, expiring token, since
    FileSystemStorage has no presign concept of its own. Swapping to a
    real S3-compatible backend later means this function calls the
    storage client's actual generate_presigned_url instead — nothing
    else in this module, or any caller, needs to change."""
    token: str = signing.dumps({"storage_key": storage_key, "action": action}, salt=LOCAL_STORAGE_SALT)
    return reverse("document-local-storage", args=[token])


def _verify_local_storage_token(token: str, action: str) -> str:
    """Used by LocalStorageView — not part of the public service
    interface (not in __all__), but colocated with _presign since it's
    the other half of the same seam."""
    payload: dict[str, Any] = signing.loads(token, salt=LOCAL_STORAGE_SALT, max_age=PRESIGN_MAX_AGE)
    if payload.get("action") != action:
        raise signing.BadSignature("token was issued for a different action")
    storage_key: str = payload["storage_key"]
    return storage_key
