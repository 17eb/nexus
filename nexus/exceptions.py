"""Shared DomainError -> HTTP mapping (CLAUDE.md: "Raise domain errors
as DomainError subclasses in services.py; a DRF exception handler maps
them to status codes. Views do not build error responses by hand.").

Lives at the project level, not inside any single app: any app's
services.py may raise a DomainError subclass without importing DRF
itself, keeping the service layer framework-agnostic. Simple lookups
(object not found) should keep using Django's get_object_or_404 instead
— DRF's default handler already turns that into a 404 with no help from
this module."""

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_exception_handler


class DomainError(Exception):
    """Base for business-rule errors that must reach the HTTP boundary
    with a specific status code. Subclasses set `status_code`."""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


def handle_domain_error(exc, context):
    if isinstance(exc, DomainError):
        return Response({"detail": exc.detail}, status=exc.status_code)
    return drf_default_exception_handler(exc, context)
