from django.urls import path

from . import views

app_name = "components"

urlpatterns = [
    path("", views.ComponentListView.as_view(), name="component_list"),
    path("add/", views.ComponentCreateView.as_view(), name="component_add"),
    path("<int:pk>/", views.ComponentDetailView.as_view(), name="component_detail"),
    path("<int:pk>/edit/", views.ComponentUpdateView.as_view(), name="component_edit"),
]
