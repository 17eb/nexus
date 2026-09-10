import hashlib

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404

from apps.documents import services
from apps.documents.factories import DocumentTypeFactory
from apps.registry.factories import PileFactory

pytestmark = pytest.mark.django_db


def _put_bytes(storage_key: str, data: bytes) -> None:
    default_storage.save(storage_key, ContentFile(data))


def test_request_upload_returns_storage_key_and_upload_url():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")

    result = services.request_upload(pile_id=pile.id, doc_type_code="WORKING_DRAWINGS", filename="a.pdf")

    assert result["storage_key"].startswith(f"documents/{pile.id}/{doc_type.code}/")
    assert result["storage_key"].endswith(".pdf")
    assert "upload_url" in result


def test_request_upload_unknown_pile_raises_404():
    DocumentTypeFactory(code="WORKING_DRAWINGS")
    with pytest.raises(Http404):
        services.request_upload(
            pile_id="00000000-0000-0000-0000-000000000000",
            doc_type_code="WORKING_DRAWINGS",
            filename="a.pdf",
        )


def test_request_upload_unknown_doc_type_raises_domain_error():
    pile = PileFactory()
    with pytest.raises(services.UnknownDocumentTypeError):
        services.request_upload(pile_id=pile.id, doc_type_code="NOT_A_REAL_TYPE", filename="a.pdf")


def test_confirm_upload_computes_checksum_and_size_from_stored_bytes_not_the_caller():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")
    data = b"hello pile world"
    result = services.request_upload(pile_id=pile.id, doc_type_code=doc_type.code, filename="a.pdf")
    _put_bytes(result["storage_key"], data)

    document = services.confirm_upload(
        pile_id=pile.id,
        doc_type_code=doc_type.code,
        title="Working drawing rev A",
        storage_key=result["storage_key"],
        content_type="application/pdf",
    )

    assert document.checksum_sha256 == hashlib.sha256(data).hexdigest()
    assert document.size_bytes == len(data)
    assert document.pile == pile
    assert document.doc_type == doc_type


def test_confirm_upload_without_prior_put_raises_upload_not_completed():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")
    result = services.request_upload(pile_id=pile.id, doc_type_code=doc_type.code, filename="a.pdf")

    with pytest.raises(services.UploadNotCompletedError):
        services.confirm_upload(
            pile_id=pile.id,
            doc_type_code=doc_type.code,
            title="Never uploaded",
            storage_key=result["storage_key"],
            content_type="application/pdf",
        )


def test_confirm_upload_with_supersedes_links_the_chain():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")

    first_request = services.request_upload(pile_id=pile.id, doc_type_code=doc_type.code, filename="a.pdf")
    _put_bytes(first_request["storage_key"], b"rev A")
    original = services.confirm_upload(
        pile_id=pile.id,
        doc_type_code=doc_type.code,
        title="Rev A",
        storage_key=first_request["storage_key"],
        content_type="application/pdf",
    )

    second_request = services.request_upload(pile_id=pile.id, doc_type_code=doc_type.code, filename="b.pdf")
    _put_bytes(second_request["storage_key"], b"rev B")
    newer = services.confirm_upload(
        pile_id=pile.id,
        doc_type_code=doc_type.code,
        title="Rev B",
        storage_key=second_request["storage_key"],
        content_type="application/pdf",
        supersedes=original.id,
    )

    assert newer.supersedes == original
    current = list(services.get_documents_for_pile(pile.id))
    assert current == [newer]


def test_get_documents_for_pile_unknown_pile_raises_404():
    with pytest.raises(Http404):
        list(services.get_documents_for_pile("00000000-0000-0000-0000-000000000000"))


def test_get_pile_ids_with_documents():
    pile_with_doc = PileFactory()
    pile_without_doc = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")
    result = services.request_upload(pile_id=pile_with_doc.id, doc_type_code=doc_type.code, filename="a.pdf")
    _put_bytes(result["storage_key"], b"data")
    services.confirm_upload(
        pile_id=pile_with_doc.id,
        doc_type_code=doc_type.code,
        title="A",
        storage_key=result["storage_key"],
        content_type="application/pdf",
    )

    found = services.get_pile_ids_with_documents([pile_with_doc.id, pile_without_doc.id])

    assert found == {pile_with_doc.id}


def test_build_download_url_points_at_local_storage_stand_in():
    pile = PileFactory()
    doc_type = DocumentTypeFactory(code="WORKING_DRAWINGS")
    result = services.request_upload(pile_id=pile.id, doc_type_code=doc_type.code, filename="a.pdf")
    _put_bytes(result["storage_key"], b"data")
    document = services.confirm_upload(
        pile_id=pile.id,
        doc_type_code=doc_type.code,
        title="A",
        storage_key=result["storage_key"],
        content_type="application/pdf",
    )

    url = services.build_download_url(document.id)

    assert "/documents/local-storage/" in url
