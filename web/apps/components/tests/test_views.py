import pytest
from django.urls import reverse

from apps.components.models import Category, Component


@pytest.mark.django_db
def test_component_list_filters_by_search_query(client):
    category = Category.objects.create(name="Resistors", unit="Ω")
    Component.objects.create(value="10k", category=category)
    Component.objects.create(value="100n", category=category, description="capacitor")

    response = client.get(reverse("components:component_list"), {"q": "capacitor"})

    assert response.status_code == 200
    values = [c.value for c in response.context["components"]]
    assert values == ["100n"]


@pytest.mark.django_db
def test_component_list_filters_by_category(client):
    resistors = Category.objects.create(name="Resistors", unit="Ω")
    capacitors = Category.objects.create(name="Capacitors", unit="F")
    Component.objects.create(value="10k", category=resistors)
    Component.objects.create(value="100n", category=capacitors)

    response = client.get(reverse("components:component_list"), {"category": resistors.pk})

    values = [c.value for c in response.context["components"]]
    assert values == ["10k"]


@pytest.mark.django_db
def test_component_detail_renders(client):
    category = Category.objects.create(name="Resistors", unit="Ω")
    component = Component.objects.create(value="10k", category=category)

    response = client.get(reverse("components:component_detail", kwargs={"pk": component.pk}))

    assert response.status_code == 200
    assert "10k Ω".encode() in response.content
