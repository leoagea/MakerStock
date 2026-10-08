from django.views.generic import DetailView, ListView

from .models import Cabinet, Drawer, Frame, StorageSystem


class StorageSystemListView(ListView):
    model = StorageSystem
    template_name = "storage/system_list.html"
    context_object_name = "systems"


class StorageSystemDetailView(DetailView):
    model = StorageSystem
    template_name = "storage/system_detail.html"
    context_object_name = "system"

class FrameDetailView(DetailView):
    model = Frame
    template_name = "storage/frame_detail.html"
    context_object_name = "frame"

class CabinetDetailView(DetailView):
    model = Cabinet
    template_name = "storage/cabinet_detail.html"
    context_object_name = "cabinet"


class DrawerDetailView(DetailView):
    model = Drawer
    template_name = "storage/drawer_detail.html"
    context_object_name = "drawer"
