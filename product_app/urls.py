from . import views
from django.urls import path

app_name = "product_app"

urlpatterns = [
    path("edit_product/<int:product_id>", views.edit_product, name="edit_product"),
    path(
        "remove_product/<int:product_id>",
        views.remove_product,
        name="remove_product",
    ),
    path("product", views.product, name="product"),
    path("add_new_product", views.add_new_product, name="add_new_product"),
    path(
        "edit_new_product/<int:product_id>",
        views.edit_new_product,
        name="edit_new_product",
    ),
    path(
        "delete_product/<int:product_id>", views.delete_product, name="delete_product"
    ),
    path(
        "archive_global_product/<int:product_id>",
        views.archive_global_product,
        name="archive_global_product",
    ),
]
