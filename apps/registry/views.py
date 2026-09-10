from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents import services as documents_services

from . import services
from .serializers import PackageEnvelopeSerializer, PileListSerializer


class PackagePilesView(APIView):
    """GET /api/v1/packages/{package_id}/piles

    Unauthenticated for now — check_permission() doesn't exist until M2.
    See the TODO on services.get_piles_for_package()'s queryset.
    """

    def get(self, request, package_id):
        package, piles = services.get_piles_for_package(package_id)
        piles = list(piles)
        # One extra query total, not one per pile — see
        # PileListSerializer.get_has_documents()'s comment, and
        # test_query_count_stays_flat_as_pile_count_grows.
        pile_ids_with_documents = documents_services.get_pile_ids_with_documents(
            [pile.id for pile in piles]
        )
        return Response(
            {
                "package": PackageEnvelopeSerializer(package).data,
                "piles": PileListSerializer(
                    piles, many=True, context={"pile_ids_with_documents": pile_ids_with_documents}
                ).data,
            }
        )
