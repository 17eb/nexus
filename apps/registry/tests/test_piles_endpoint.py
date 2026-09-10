import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from apps.documents.factories import DocumentFactory
from apps.registry import services
from apps.registry.factories import PackageFactory, PileCapFactory, PileFactory
from apps.registry.models import Pile, PileCap

from .helpers import ASBUILT_HEADERS, DESIGN_HEADERS, asbuilt_row, design_row, make_csv_bytes

pytestmark = pytest.mark.django_db


def piles_url(package_id) -> str:
    return reverse("package-piles", kwargs={"package_id": package_id})


def test_envelope_carries_package_crs_epsg_and_chainage_bearing():
    package = PackageFactory(crs_epsg=3123, chainage_bearing="180.000")
    client = APIClient()

    response = client.get(piles_url(package.id))

    assert response.status_code == 200
    assert response.json()["package"] == {"crs_epsg": 3123, "chainage_bearing": "180.000"}


def test_design_only_pile_reports_design_source():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="design.csv",
        apply=True,
    )
    client = APIClient()

    response = client.get(piles_url(package.id))

    assert response.status_code == 200
    pile = response.json()["piles"][0]
    assert pile["pile_no"] == "P-1"
    assert pile["diameter_mm"] == 1500
    assert pile["coordinates"] == {"source": "design", "e": "498000.000", "n": "1557000.000"}


def test_asbuilt_pile_reports_asbuilt_source_not_design():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(DESIGN_HEADERS, [design_row(pile_no="P-1", label="A")]),
        filename="design.csv",
        apply=True,
    )
    services.import_piles(
        package=package,
        coordinate_type="as_built",
        file_obj=make_csv_bytes(ASBUILT_HEADERS, [asbuilt_row(pile_no="P-1")]),
        filename="asbuilt.csv",
        apply=True,
    )
    client = APIClient()

    response = client.get(piles_url(package.id))

    pile = response.json()["piles"][0]
    assert pile["coordinates"] == {"source": "as_built", "e": "498000.030", "n": "1556999.980"}


def test_pile_cap_and_structure_nested_fields():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [
                design_row(
                    pile_no="P-1",
                    label="A",
                    structure_ref="PR07",
                    structure_kind="station",
                    pile_cap_ref="2",
                    cap_type="straddle",
                )
            ],
        ),
        filename="design.csv",
        apply=True,
    )
    client = APIClient()

    response = client.get(piles_url(package.id))

    pile = response.json()["piles"][0]
    pile_cap = PileCap.objects.get(structure__package=package, ref="2")
    assert pile["pile_cap"] == {
        "id": str(pile_cap.id),
        "ref": "2",
        "cap_type": "straddle",
    }
    assert pile["structure"] == {
        "id": str(pile_cap.structure.id),
        "ref": "PR07",
        "kind": "station",
    }


def test_has_documents_reflects_document_presence():
    package = PackageFactory(crs_epsg=3123)
    services.import_piles(
        package=package,
        coordinate_type="design",
        file_obj=make_csv_bytes(
            DESIGN_HEADERS,
            [
                design_row(pile_no="P-1", label="A", pile_cap_ref="1"),
                design_row(pile_no="P-2", label="B", pile_cap_ref="1"),
            ],
        ),
        filename="design.csv",
        apply=True,
    )
    pile_with_doc = Pile.objects.get(pile_no="P-1")
    DocumentFactory(pile=pile_with_doc)
    client = APIClient()

    response = client.get(piles_url(package.id))

    by_pile_no = {p["pile_no"]: p["has_documents"] for p in response.json()["piles"]}
    assert by_pile_no == {"P-1": True, "P-2": False}


def test_unknown_package_returns_404():
    client = APIClient()
    response = client.get(piles_url(uuid.uuid4()))
    assert response.status_code == 404


def test_package_with_no_piles_returns_empty_list_not_error():
    package = PackageFactory(crs_epsg=3123)
    client = APIClient()

    response = client.get(piles_url(package.id))

    assert response.status_code == 200
    assert response.json()["piles"] == []


def test_no_auth_required():
    package = PackageFactory(crs_epsg=3123)
    client = APIClient()  # no credentials, no session

    response = client.get(piles_url(package.id))

    assert response.status_code == 200


def test_query_count_stays_flat_as_pile_count_grows():
    package = PackageFactory(crs_epsg=3123)
    cap = PileCapFactory(structure__package=package)
    PileFactory(pile_cap=cap, pile_no="P-1", label="A")
    client = APIClient()

    with CaptureQueriesContext(connection) as first:
        response = client.get(piles_url(package.id))
    assert response.status_code == 200
    baseline = len(first.captured_queries)

    cap2 = PileCapFactory(structure__package=package)
    for i, label in enumerate("BCDEFGHI"):
        PileFactory(pile_cap=cap2, pile_no=f"P-{i + 2}", label=label)

    with CaptureQueriesContext(connection) as second:
        response = client.get(piles_url(package.id))
    assert response.status_code == 200
    assert len(response.json()["piles"]) == 9
    assert len(second.captured_queries) == baseline
