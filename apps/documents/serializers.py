from rest_framework import serializers

from .models import Document, DocumentType


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ["code", "name", "sort_order", "requires_revision"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "content_type", "size_bytes", "uploaded_at"]


class UploadRequestSerializer(serializers.Serializer):
    pile_id = serializers.UUIDField()
    doc_type_code = serializers.CharField()
    filename = serializers.CharField()


class ConfirmUploadSerializer(serializers.Serializer):
    pile_id = serializers.UUIDField()
    doc_type_code = serializers.CharField()
    title = serializers.CharField()
    storage_key = serializers.CharField()
    content_type = serializers.CharField()
    supersedes = serializers.UUIDField(required=False, allow_null=True)
