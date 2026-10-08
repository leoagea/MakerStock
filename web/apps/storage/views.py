from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import CabinetForm, FrameForm
from .models import Cabinet, Drawer, Frame, StorageSystem
from .services import frame_bounding_box, generate_drawers_for_cabinet


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


class System3DView(StorageSidebarMixin, DetailView):
    model = StorageSystem
    template_name = "storage/system_3d.html"
    context_object_name = "system"

    def get_current_system(self):
        return self.object


class SystemVisualizationDataView(View):
    """JSON for the system-level 3D overview: each frame as a single box,
    sized from the bounding box of its cabinets (see frame_bounding_box).
    Clicking a frame in the scene navigates to its own 3D view (the `url`
    below), which shows its cabinets/drawers in full."""

    def get(self, request, pk):
        system = get_object_or_404(StorageSystem, pk=pk)
        frames = [
            {
                "id": frame.pk,
                "code": frame.code,
                "name": frame.name,
                "cabinet_count": frame.cabinets.count(),
                "dimensions": frame_bounding_box(frame),
                "url": reverse("storage:frame_3d", kwargs={"pk": frame.pk}),
            }
            for frame in system.frames.all()
        ]
        return JsonResponse({"id": system.pk, "name": system.name, "frames": frames})


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


class Frame3DView(StorageSidebarMixin, DetailView):
    model = Frame
    template_name = "storage/frame_3d.html"
    context_object_name = "frame"

    def get_current_system(self):
        return self.object.system

    def get_current_frame(self):
        return self.object


class FrameVisualizationDataView(View):
    """JSON for the 3D visualizer: the frame's cabinets with their physical
    position/dimensions, and each cabinet's drawers with their grid position.
    All physical values are in millimeters — see Cabinet's docstring for the
    coordinate system."""

    def get(self, request, pk):
        frame = get_object_or_404(Frame, pk=pk)
        cabinets = []
        for cabinet in frame.cabinets.all():
            drawers = [
                {
                    "id": drawer.pk,
                    "code": drawer.code,
                    "column": drawer.column,
                    "row": drawer.row,
                    "component_count": drawer.stock_entries.count(),
                }
                for drawer in cabinet.drawers.all()
            ]
            cabinets.append(
                {
                    "id": cabinet.pk,
                    "code": cabinet.code,
                    "name": cabinet.name,
                    "position": {
                        "x": cabinet.position_x,
                        "y": cabinet.position_y,
                        "z": cabinet.position_z,
                    },
                    "dimensions": {
                        "width": cabinet.width,
                        "height": cabinet.height,
                        "depth": cabinet.depth,
                    },
                    "grid": {"columns": cabinet.column, "rows": cabinet.row},
                    "drawers": drawers,
                }
            )

        return JsonResponse(
            {
                "id": frame.pk,
                "code": frame.code,
                "name": frame.name,
                "system": frame.system.name,
                "cabinets": cabinets,
            }
        )


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

    def form_valid(self, form):
        response = super().form_valid(form)
        generate_drawers_for_cabinet(self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("storage:cabinet_detail", kwargs={"pk": self.object.pk})
