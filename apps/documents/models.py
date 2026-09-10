import uuid

from django.db import models


class DocumentType(models.Model):
    """Reference data — the nine sections a user sees on a pile record
    (docs/domain.md), plus whatever gets added later. `sort_order` is
    the display order; the table deliberately doesn't assume nine is the
    maximum."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    sort_order = models.PositiveSmallIntegerField()
    requires_revision = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    """File bytes are never overwritten (CLAUDE.md) — a new version is a
    new row with `supersedes` set, never an edit to an existing row.

    `pile` is a string FK ("registry.Pile") rather than an import of
    apps.registry.models — this is a real FK relationship that still
    respects the module-boundary rule (no cross-app model imports).

    No `uploaded_by` in M1: docs/mvp-plan.md's M2 introduces its own
    `identity.User`, not obviously a thin wrapper on
    `django.contrib.auth.User`. Adding the FK now against the wrong
    target is the same mistake `Package.holiday_calendar` already
    avoided once — add it in M2 alongside the model it actually points
    to."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pile = models.ForeignKey(
        "registry.Pile", on_delete=models.PROTECT, null=True, blank=True, related_name="documents"
    )
    doc_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, related_name="documents")
    title = models.CharField(max_length=255)
    # Object storage key. Unique so a repeated confirm_upload() against
    # the same uploaded object can't silently create two rows over one
    # set of bytes (services.py is deliberately stateless between
    # request_upload() and confirm_upload() — this constraint is what
    # keeps that safe).
    storage_key = models.CharField(max_length=500, unique=True)
    checksum_sha256 = models.CharField(max_length=64)
    size_bytes = models.PositiveBigIntegerField()
    content_type = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    supersedes = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="superseded_by"
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.doc_type})"
