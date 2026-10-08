from django.urls import path

from . import views

app_name = "storage"

urlpatterns = [
    path("", views.StorageSystemListView.as_view(), name="system_list"),
    path("systems/<int:pk>/", views.StorageSystemDetailView.as_view(), name="system_detail"),
    path("frames/add/", views.FrameCreateView.as_view(), name="frame_add"),
    path("frames/<int:pk>/", views.FrameDetailView.as_view(), name="frame_detail"),
    path("cabinets/add/", views.CabinetCreateView.as_view(), name="cabinet_add"),
    path("cabinets/<int:pk>/", views.CabinetDetailView.as_view(), name="cabinet_detail"),
    path("drawers/<int:pk>/", views.DrawerDetailView.as_view(), name="drawer_detail"),
]
