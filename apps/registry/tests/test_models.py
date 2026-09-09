import decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.registry.factories import (
    PackageFactory,
    PileCapFactory,
    PileFactory,
    StructureFactory,
)
from apps.registry.models import Structure

pytestmark = pytest.mark.django_db


def test_pile_no_globally_unique():
    cap_a = PileCapFactory()
    cap_b = PileCapFactory()
    PileFactory(pile_cap=cap_a, pile_no="P-1", label="A")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            PileFactory(pile_cap=cap_b, pile_no="P-1", label="A")


def test_label_unique_within_cap_but_not_across_caps():
    cap_a = PileCapFactory()
    cap_b = PileCapFactory()
    PileFactory(pile_cap=cap_a, label="A", pile_no="P-1")
    # same label in a different cap is fine
    PileFactory(pile_cap=cap_b, label="A", pile_no="P-2")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            PileFactory(pile_cap=cap_a, label="A", pile_no="P-3")


def test_structure_ref_unique_within_package():
    package = PackageFactory()
    StructureFactory(package=package, ref="PR01")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            StructureFactory(package=package, ref="PR01")


def test_pilecap_ref_unique_within_structure():
    structure = StructureFactory()
    PileCapFactory(structure=structure, ref="1")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            PileCapFactory(structure=structure, ref="1")


def test_decimal_precision_rounds_to_declared_places():
    pile = PileFactory(design_e=decimal.Decimal("500000.12349"))
    pile.refresh_from_db()
    assert pile.design_e == decimal.Decimal("500000.123")


def test_protect_blocks_deletion_of_package_with_structures():
    structure = StructureFactory()
    with pytest.raises(ProtectedError):
        structure.package.delete()


def test_protect_blocks_deletion_of_structure_with_caps():
    cap = PileCapFactory()
    with pytest.raises(ProtectedError):
        cap.structure.delete()


def test_protect_blocks_deletion_of_pilecap_with_piles():
    pile = PileFactory()
    with pytest.raises(ProtectedError):
        pile.pile_cap.delete()


def test_timestamps_set_on_create_and_update():
    pile = PileFactory()
    assert pile.created_at is not None
    assert pile.updated_at is not None
    original_updated_at = pile.updated_at
    pile.diameter_mm = 1200
    pile.save()
    pile.refresh_from_db()
    assert pile.updated_at > original_updated_at


def test_str_representations():
    package = PackageFactory(code="S-05", name="Package 5")
    structure = StructureFactory(package=package, ref="PR01")
    cap = PileCapFactory(structure=structure, ref="1")
    pile = PileFactory(pile_cap=cap, pile_no="P-1045S")

    assert str(package) == "S-05 — Package 5"
    assert str(structure) == "S-05/PR01"
    assert str(cap) == "S-05/PR01/1"
    assert "P-1045S" in str(pile)


def test_structure_kind_choices():
    assert Structure.Kind.VIADUCT == "viaduct"
    assert Structure.Kind.STATION == "station"
