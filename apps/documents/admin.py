from django.contrib import admin

from .models import Document, DocumentType


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "sort_order", "requires_revision"]
    ordering = ["sort_order"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "doc_type",
        "pile",
        "storage_key",
        "size_bytes",
        "uploaded_at",
        "supersedes",
    ]
    list_filter = ["doc_type"]
    search_fields = ["title", "storage_key", "pile__pile_no"]
    readonly_fields = [f.name for f in Document._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # docs/permissions.md: "No role can delete a Document ... .
        # Supersession only."
        return False
