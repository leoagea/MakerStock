from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import CabinetForm, FrameForm
from .models import Cabinet, Drawer, Frame, StorageSystem


class StorageSidebarMixin:
    """Supplies the sidebar's system switcher and frame/cabinet tree context,
    shared by every storage page via storage/_storage_base.html."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_systems"] = StorageSystem.objects.all()
        context["current_system"] = self.get_current_system()
        context["current_frame"] = self.get_current_frame()
        return context

    def get_current_system(self):
        return None

    def get_current_frame(self):
        return None


class StorageSystemListView(StorageSidebarMixin, ListView):
    model = StorageSystem
    template_name = "storage/system_list.html"
    context_object_name = "systems"


class StorageSystemDetailView(StorageSidebarMixin, DetailView):
    model = StorageSystem
    template_name = "storage/system_detail.html"
    context_object_name = "system"

    def get_current_system(self):
        return self.object


class FrameDetailView(StorageSidebarMixin, DetailView):
    model = Frame
    template_name = "storage/frame_detail.html"
    context_object_name = "frame"

    def get_current_system(self):
        return self.object.system

    def get_current_frame(self):
        return self.object


class CabinetDetailView(StorageSidebarMixin, DetailView):
    model = Cabinet
    template_name = "storage/cabinet_detail.html"
    context_object_name = "cabinet"

    def get_current_system(self):
        return self.object.frame.system

    def get_current_frame(self):
        return self.object.frame


class DrawerDetailView(StorageSidebarMixin, DetailView):
    model = Drawer
    template_name = "storage/drawer_detail.html"
    context_object_name = "drawer"

    def get_current_system(self):
        return self.object.cabinet.frame.system

    def get_current_frame(self):
        return self.object.cabinet.frame


class FrameCreateView(StorageSidebarMixin, CreateView):
    model = Frame
    form_class = FrameForm
    template_name = "storage/frame_form.html"

    def get_initial(self):
        initial = super().get_initial()
        system_id = self.request.GET.get("system")
        if system_id:
            initial["system"] = system_id
        return initial

    def get_current_system(self):
        system_id = self.request.GET.get("system")
        return StorageSystem.objects.filter(pk=system_id).first() if system_id else None

    def get_success_url(self):
        return reverse_lazy("storage:frame_detail", kwargs={"pk": self.object.pk})


class CabinetCreateView(StorageSidebarMixin, CreateView):
    model = Cabinet
    form_class = CabinetForm
    template_name = "storage/cabinet_form.html"

    def get_initial(self):
        initial = super().get_initial()
        frame_id = self.request.GET.get("frame")
        if frame_id:
            initial["frame"] = frame_id
        return initial

    def get_current_frame(self):
        frame_id = self.request.GET.get("frame")
        return Frame.objects.filter(pk=frame_id).first() if frame_id else None

    def get_current_system(self):
        frame = self.get_current_frame()
        return frame.system if frame else None

    def get_success_url(self):
        return reverse_lazy("storage:cabinet_detail", kwargs={"pk": self.object.pk})
