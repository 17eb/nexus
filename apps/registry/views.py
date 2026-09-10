from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import PackageEnvelopeSerializer, PileListSerializer


class PackagePilesView(APIView):
    """GET /api/v1/packages/{package_id}/piles

    Unauthenticated for now — check_permission() doesn't exist until M2.
    See the TODO on services.get_piles_for_package()'s queryset.
    """

    def get(self, request, package_id):
        package, piles = services.get_piles_for_package(package_id)
        return Response(
            {
                "package": PackageEnvelopeSerializer(package).data,
                "piles": PileListSerializer(piles, many=True).data,
            }
        )
