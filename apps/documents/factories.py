import factory
from factory.django import DjangoModelFactory

from .models import Document, DocumentType


class DocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = DocumentType
        django_get_or_create = ["code"]

    code = factory.Sequence(lambda n: f"DOC_TYPE_{n}")
    name = factory.Sequence(lambda n: f"Document type {n}")
    sort_order = factory.Sequence(lambda n: n)
    requires_revision = False


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    doc_type = factory.SubFactory(DocumentTypeFactory)
    title = factory.Sequence(lambda n: f"Document {n}")
    storage_key = factory.Sequence(lambda n: f"documents/test/{n}.pdf")
    checksum_sha256 = "0" * 64
    size_bytes = 1024
    content_type = "application/pdf"
