import uuid

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.documents.factories import DocumentTypeFactory
from apps.registry.factories import PileFactory

pytestmark = pytest.mark.django_db


def test_full_upload_confirm_download_round_trip():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS", sort_order=1)
    client = APIClient()

    request_response = client.post(
        reverse("document-upload-request"),
        {"pile_id": str(pile.id), "doc_type_code": doc_type.code, "filename": "drawing.pdf"},
        format="json",
    )
    assert request_response.status_code == 201
    storage_key = request_response.json()["storage_key"]
    upload_url = request_response.json()["upload_url"]

    put_response = client.put(upload_url, data=b"%PDF-1.4 fake pdf bytes", content_type="application/pdf")
    assert put_response.status_code == 204

    confirm_response = client.post(
        reverse("document-confirm"),
        {
            "pile_id": str(pile.id),
            "doc_type_code": doc_type.code,
            "title": "Working drawing rev A",
            "storage_key": storage_key,
            "content_type": "application/pdf",
        },
        format="json",
    )
    assert confirm_response.status_code == 201
    document_id = confirm_response.json()["id"]

    documents_response = client.get(reverse("pile-documents", kwargs={"pile_id": pile.id}))
    assert documents_response.status_code == 200
    body = documents_response.json()
    assert body["pile_id"] == str(pile.id)
    section = next(s for s in body["sections"] if s["doc_type"]["code"] == doc_type.code)
    assert [d["title"] for d in section["documents"]] == ["Working drawing rev A"]

    download_response = client.get(
        reverse("document-download", kwargs={"document_id": document_id}), follow=False
    )
    assert download_response.status_code == 302
    redirected = client.get(download_response.url)
    assert redirected.status_code == 200
    assert b"".join(redirected.streaming_content) == b"%PDF-1.4 fake pdf bytes"


def test_pile_documents_lists_all_nine_sections_with_empty_states():
    pile = PileFactory()
    client = APIClient()

    response = client.get(reverse("pile-documents", kwargs={"pile_id": pile.id}))

    assert response.status_code == 200
    sections = response.json()["sections"]
    assert len(sections) == 9
    assert all(section["documents"] == [] for section in sections)
    assert [s["doc_type"]["sort_order"] for s in sections] == list(range(1, 10))


def test_pile_documents_unknown_pile_returns_404():
    client = APIClient()
    response = client.get(reverse("pile-documents", kwargs={"pile_id": uuid.uuid4()}))
    assert response.status_code == 404


def test_upload_request_unknown_doc_type_returns_400():
    pile = PileFactory()
    client = APIClient()

    response = client.post(
        reverse("document-upload-request"),
        {"pile_id": str(pile.id), "doc_type_code": "NOT_REAL", "filename": "a.pdf"},
        format="json",
    )

    assert response.status_code == 400


def test_confirm_before_put_returns_409():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")
    client = APIClient()

    request_response = client.post(
        reverse("document-upload-request"),
        {"pile_id": str(pile.id), "doc_type_code": doc_type.code, "filename": "a.pdf"},
        format="json",
    )
    storage_key = request_response.json()["storage_key"]

    confirm_response = client.post(
        reverse("document-confirm"),
        {
            "pile_id": str(pile.id),
            "doc_type_code": doc_type.code,
            "title": "Never uploaded",
            "storage_key": storage_key,
            "content_type": "application/pdf",
        },
        format="json",
    )

    assert confirm_response.status_code == 409


def test_local_storage_view_rejects_tampered_token():
    client = APIClient()
    response = client.get(
        reverse("document-local-storage", kwargs={"token": "not-a-real-token"})
    )
    assert response.status_code == 400


def test_no_auth_required():
    # Unauthenticated for now — check_permission() doesn't exist until
    # M2, same precedent as registry's PackagePilesView. Pins today's
    # open behavior so an accidental lock-down fails loudly.
    pile = PileFactory()
    client = APIClient()
    response = client.get(reverse("pile-documents", kwargs={"pile_id": pile.id}))
    assert response.status_code == 200
