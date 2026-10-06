from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import InventoryForm
from .models import Inventory


class InventoryCreateView(CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"

    def get_initial(self):
        initial = super().get_initial()
        component_id = self.request.GET.get("component")
        drawer_id = self.request.GET.get("drawer")
        if component_id:
            initial["component"] = component_id
        if drawer_id:
            initial["drawer"] = drawer_id
        return initial

    def get_success_url(self):
        return reverse_lazy("components:component_detail", kwargs={"pk": self.object.component_id})


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"

    def get_success_url(self):
        return reverse_lazy("components:component_detail", kwargs={"pk": self.object.component_id})
