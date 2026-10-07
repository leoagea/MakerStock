from django.views.generic import TemplateView

from apps.components.models import Component
from apps.inventory.services import low_stock_entries
from apps.storage.models import Drawer


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["component_count"] = Component.objects.count()
        context["drawer_count"] = Drawer.objects.count()
        context["low_stock_entries"] = low_stock_entries()
        return context
