import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.documents.factories import DocumentFactory, DocumentTypeFactory
from apps.documents.models import DocumentType
from apps.registry.factories import PileFactory

pytestmark = pytest.mark.django_db


def test_nine_sections_seeded_in_sort_order():
    codes_in_order = list(DocumentType.objects.order_by("sort_order").values_list("code", flat=True))
    assert codes_in_order == [
        "GEOTECHNICAL_REPORTS",
        "BORED_PILE_RECORDS",
        "CONCRETE_RECORDS",
        "SLURRY_SAMPLE",
        "COMPRESSIVE_STRENGTH_TEST_RESULTS",
        "ASBUILT_SURVEY_REPORT",
        "WORKING_DRAWINGS",
        "FIELD_DATA_SHEET",
        "DEEP_FOUNDATION_TEST_REPORTS",
    ]


def test_document_type_code_unique():
    # Bypasses the factory's get_or_create (needed elsewhere so tests can
    # reuse the migration-seeded codes, e.g. "WORKING_DRAWINGS", without
    # colliding with them) to actually exercise the uniqueness constraint.
    DocumentType.objects.create(code="DUP", name="Duplicate", sort_order=999)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            DocumentType.objects.create(code="DUP", name="Duplicate again", sort_order=1000)


def test_storage_key_unique():
    DocumentFactory(storage_key="documents/dup.pdf")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            DocumentFactory(storage_key="documents/dup.pdf")


def test_pile_nullable():
    document = DocumentFactory(pile=None)
    assert document.pile is None


def test_protect_blocks_deletion_of_doc_type_with_documents():
    doc_type = DocumentTypeFactory()
    DocumentFactory(doc_type=doc_type)
    with pytest.raises(ProtectedError):
        doc_type.delete()


def test_protect_blocks_deletion_of_pile_with_documents():
    pile = PileFactory()
    DocumentFactory(pile=pile)
    with pytest.raises(ProtectedError):
        pile.delete()


def test_supersedes_reverse_accessor_is_superseded_by():
    original = DocumentFactory()
    newer = DocumentFactory(supersedes=original)

    assert newer.supersedes == original
    assert list(original.superseded_by.all()) == [newer]
    assert newer.superseded_by.count() == 0


def test_protect_blocks_deletion_of_superseded_document():
    original = DocumentFactory()
    DocumentFactory(supersedes=original)
    with pytest.raises(ProtectedError):
        original.delete()
