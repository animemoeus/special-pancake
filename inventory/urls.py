from django.urls import path

from inventory.views import ProductCreateView
from inventory.views import ProductDeleteView
from inventory.views import ProductListView
from inventory.views import ProductUpdateView

app_name = "inventory"


urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("product/create/", ProductCreateView.as_view(), name="product-create"),
    path(
        "product/<int:product_id>/update/",
        ProductUpdateView.as_view(),
        name="product-update",
    ),
    path(
        "product/<int:product_id>/delete/",
        ProductDeleteView.as_view(),
        name="product-delete",
    ),
]
