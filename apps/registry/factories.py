import factory
from factory.django import DjangoModelFactory

from .models import Package, Pile, PileCap, Structure


class PackageFactory(DjangoModelFactory):
    class Meta:
        model = Package

    code = factory.Sequence(lambda n: f"S-{n:02d}")
    name = factory.Faker("city")
    crs_epsg = 3123
    chainage_bearing = "180.000"


class StructureFactory(DjangoModelFactory):
    class Meta:
        model = Structure

    package = factory.SubFactory(PackageFactory)
    kind = Structure.Kind.VIADUCT
    ref = factory.Sequence(lambda n: f"PR{n}")
    name = ""


class PileCapFactory(DjangoModelFactory):
    class Meta:
        model = PileCap

    structure = factory.SubFactory(StructureFactory)
    ref = factory.Sequence(lambda n: f"CAP{n}")
    cap_type = PileCap.CapType.STANDARD
    top_level = None


class PileFactory(DjangoModelFactory):
    class Meta:
        model = Pile

    pile_cap = factory.SubFactory(PileCapFactory)
    label = factory.Sequence(lambda n: "ABCDEFGHI"[n % 9])
    pile_no = factory.Sequence(lambda n: f"P-{1000 + n}")
    diameter_mm = 1500
    design_length_m = "25.000"
    design_e = "500000.000"
    design_n = "1560000.000"
    cutoff_level = "10.500"
    tip_elevation = "-14.500"
