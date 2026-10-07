import pytest
from django.urls import reverse

from apps.components.models import Category, Component
from apps.inventory.models import Inventory
from apps.storage.models import Cabinet, Drawer, StorageSystem


@pytest.mark.django_db
def test_dashboard_shows_counts_and_low_stock(client):
    system = StorageSystem.objects.create(name="Workshop")
    cabinet = Cabinet.objects.create(system=system, code="A")
    drawer = Drawer.objects.create(cabinet=cabinet, code="D-042")
    category = Category.objects.create(name="Resistors", unit="Ω")
    component = Component.objects.create(value="10k", category=category)
    Inventory.objects.create(component=component, drawer=drawer, quantity=2, low_stock_threshold=5)

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"1 component" in response.content
    assert b"1 drawer" in response.content
    assert b"10k" in response.content
    assert b"qty 2" in response.content


@pytest.mark.django_db
def test_dashboard_shows_empty_state_when_nothing_is_low(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Nothing is low on stock." in response.content
