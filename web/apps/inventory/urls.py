from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("add/", views.InventoryCreateView.as_view(), name="inventory_add"),
    path("<int:pk>/edit/", views.InventoryUpdateView.as_view(), name="inventory_edit"),
]
