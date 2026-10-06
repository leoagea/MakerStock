from django.urls import path

from . import views

app_name = "storage"

urlpatterns = [
    path("", views.StorageSystemListView.as_view(), name="system_list"),
    path("systems/<int:pk>/", views.StorageSystemDetailView.as_view(), name="system_detail"),
    path("cabinets/<int:pk>/", views.CabinetDetailView.as_view(), name="cabinet_detail"),
    path("drawers/<int:pk>/", views.DrawerDetailView.as_view(), name="drawer_detail"),
]
