from django.contrib import admin

from .models import ImportRun, Package, Pile, PileCap, Structure


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "crs_epsg", "chainage_bearing"]
    search_fields = ["code", "name"]


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ["ref", "package", "kind", "name"]
    list_filter = ["kind", "package"]
    search_fields = ["ref", "name"]


@admin.register(PileCap)
class PileCapAdmin(admin.ModelAdmin):
    list_display = ["ref", "structure", "cap_type", "top_level"]
    list_filter = ["cap_type"]
    search_fields = ["ref"]


@admin.register(Pile)
class PileAdmin(admin.ModelAdmin):
    list_display = [
        "pile_no",
        "pile_cap",
        "label",
        "diameter_mm",
        "design_e",
        "design_n",
        "asbuilt_e",
        "asbuilt_n",
    ]
    search_fields = ["pile_no"]
    list_filter = ["pile_cap__structure__package"]


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = [
        "package",
        "coordinate_type",
        "filename",
        "created_count",
        "updated_count",
        "changed_count",
        "errored_count",
        "created_at",
    ]
    list_filter = ["coordinate_type", "package"]
    readonly_fields = [f.name for f in ImportRun._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
