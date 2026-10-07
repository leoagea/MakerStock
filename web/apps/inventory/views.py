from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
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


class InventoryQuantityUpdateView(View):
    """HTMX endpoint: updates an entry's quantity in place and re-renders its row."""

    def post(self, request, pk):
        entry = get_object_or_404(Inventory, pk=pk)
        try:
            quantity = int(request.POST.get("quantity", ""))
        except (TypeError, ValueError):
            quantity = None

        if quantity is not None and quantity >= 0:
            entry.quantity = quantity
            entry.save(update_fields=["quantity"])

        show = request.GET.get("show", "drawer")
        return render(request, "inventory/_stock_entry_row.html", {"entry": entry, "show": show})


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = "inventory/inventory_form.html"

    def get_success_url(self):
        return reverse_lazy("components:component_detail", kwargs={"pk": self.object.component_id})
