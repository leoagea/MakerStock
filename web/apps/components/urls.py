from django.urls import path

from . import views

app_name = "components"

urlpatterns = [
    path("", views.ComponentListView.as_view(), name="component_list"),
    path("add/", views.ComponentCreateView.as_view(), name="component_add"),
    path("catalog-admin/", views.CatalogAdminView.as_view(), name="catalog_admin"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path(
        "manufacturers/<int:pk>/edit/",
        views.ManufacturerUpdateView.as_view(),
        name="manufacturer_edit",
    ),
    path("<int:pk>/", views.ComponentDetailView.as_view(), name="component_detail"),
    path("<int:pk>/edit/", views.ComponentUpdateView.as_view(), name="component_edit"),
]
