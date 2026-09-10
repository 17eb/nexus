from django.urls import path

from .views import PackagePilesView

urlpatterns = [
    path("packages/<uuid:package_id>/piles", PackagePilesView.as_view(), name="package-piles"),
]
