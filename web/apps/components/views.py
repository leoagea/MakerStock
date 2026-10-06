from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ComponentForm
from .models import Category, Component, Manufacturer


class ComponentListView(ListView):
    model = Component
    template_name = "components/component_list.html"
    context_object_name = "components"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category", "manufacturer")
        query = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category", "").strip()
        manufacturer_id = self.request.GET.get("manufacturer", "").strip()

        if query:
            queryset = queryset.filter(
                Q(value__icontains=query)
                | Q(manufacturer_part_number__icontains=query)
                | Q(description__icontains=query)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if manufacturer_id:
            queryset = queryset.filter(manufacturer_id=manufacturer_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["manufacturers"] = Manufacturer.objects.all()
        context["query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_manufacturer"] = self.request.GET.get("manufacturer", "")
        return context


class ComponentDetailView(DetailView):
    model = Component
    template_name = "components/component_detail.html"
    context_object_name = "component"


class ComponentCreateView(CreateView):
    model = Component
    form_class = ComponentForm
    template_name = "components/component_form.html"

    def get_success_url(self):
        return reverse_lazy("components:component_detail", kwargs={"pk": self.object.pk})


class ComponentUpdateView(UpdateView):
    model = Component
    form_class = ComponentForm
    template_name = "components/component_form.html"

    def get_success_url(self):
        return reverse_lazy("components:component_detail", kwargs={"pk": self.object.pk})
