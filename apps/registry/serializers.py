from rest_framework import serializers

from .models import Package, Pile


class PackageEnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ["crs_epsg", "chainage_bearing"]


class PileListSerializer(serializers.ModelSerializer):
    pile_cap = serializers.SerializerMethodField()
    structure = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    has_documents = serializers.SerializerMethodField()

    class Meta:
        model = Pile
        fields = [
            "id",
            "pile_no",
            "label",
            "diameter_mm",
            "pile_cap",
            "structure",
            "coordinates",
            "has_documents",
        ]

    def get_pile_cap(self, obj: Pile) -> dict:
        return {
            "id": str(obj.pile_cap.id),
            "ref": obj.pile_cap.ref,
            "cap_type": obj.pile_cap.cap_type,
        }

    def get_structure(self, obj: Pile) -> dict:
        structure = obj.pile_cap.structure
        return {"id": str(structure.id), "ref": structure.ref, "kind": structure.kind}

    def get_coordinates(self, obj: Pile) -> dict:
        # Explicit str() — unlike a declared DecimalField, a raw Decimal
        # returned from a SerializerMethodField bypasses DRF's normal
        # coerce-to-string behavior and falls through to float(), which
        # silently drops precision (e.g. "498000.030" -> 498000.03).
        return {
            "source": obj.coordinate_source,
            "e": str(obj.display_e),
            "n": str(obj.display_n),
        }

    def get_has_documents(self, obj: Pile) -> bool:
        # Batched once per request into context by the view — never a
        # per-pile query. See PackagePilesView.get().
        return obj.id in self.context.get("pile_ids_with_documents", set())
