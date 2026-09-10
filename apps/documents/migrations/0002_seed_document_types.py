from django.db import migrations

# The nine sections a user sees on a pile record, in order
# (docs/domain.md). `requires_revision` defaults to False for all nine —
# domain.md doesn't say which (if any) need revision tracking, so this
# defaults rather than guesses; it's editable reference data, not a
# structural decision.
DOCUMENT_TYPES = [
    ("GEOTECHNICAL_REPORTS", "Geotechnical reports"),
    ("BORED_PILE_RECORDS", "Bored pile records"),
    ("CONCRETE_RECORDS", "Concrete records"),
    ("SLURRY_SAMPLE", "Slurry sample"),
    ("COMPRESSIVE_STRENGTH_TEST_RESULTS", "Compressive strength test results"),
    ("ASBUILT_SURVEY_REPORT", "Bored pile as-built survey report"),
    ("WORKING_DRAWINGS", "Working drawings"),
    ("FIELD_DATA_SHEET", "Field data sheet"),
    ("DEEP_FOUNDATION_TEST_REPORTS", "Deep foundation test reports / pile test reports"),
]


def seed_document_types(apps, schema_editor):
    DocumentType = apps.get_model("documents", "DocumentType")
    for sort_order, (code, name) in enumerate(DOCUMENT_TYPES, start=1):
        DocumentType.objects.update_or_create(
            code=code, defaults={"name": name, "sort_order": sort_order}
        )


def unseed_document_types(apps, schema_editor):
    DocumentType = apps.get_model("documents", "DocumentType")
    DocumentType.objects.filter(code__in=[code for code, _ in DOCUMENT_TYPES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_document_types, unseed_document_types),
    ]
