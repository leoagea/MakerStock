from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CategoryForm, ComponentForm, ManufacturerForm
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


class CatalogAdminView(View):
    """One page to add/browse Category and Manufacturer — the reference data
    components are built from. Everything else about them (parenting,
    cleanup) stays in the Django admin; this just covers the common case of
    adding a new one without leaving the app.
    """

    template_name = "components/catalog_admin.html"

    def get(self, request):
        return self._render(request, CategoryForm(), ManufacturerForm())

    def post(self, request):
        action = request.POST.get("action")
        category_form = CategoryForm()
        manufacturer_form = ManufacturerForm()

        if action == "add_category":
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect("components:catalog_admin")
        elif action == "add_manufacturer":
            manufacturer_form = ManufacturerForm(request.POST)
            if manufacturer_form.is_valid():
                manufacturer_form.save()
                return redirect("components:catalog_admin")

        return self._render(request, category_form, manufacturer_form)

    def _render(self, request, category_form, manufacturer_form):
        return render(
            request,
            self.template_name,
            {
                "categories": Category.objects.all(),
                "manufacturers": Manufacturer.objects.all(),
                "category_form": category_form,
                "manufacturer_form": manufacturer_form,
            },
        )


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "components/category_form.html"
    success_url = reverse_lazy("components:catalog_admin")


class ManufacturerUpdateView(UpdateView):
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = "components/manufacturer_form.html"
    success_url = reverse_lazy("components:catalog_admin")
