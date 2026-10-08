import pytest
from django.urls import reverse

from apps.components.models import Category, Component
from apps.inventory.models import Inventory
from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem


@pytest.fixture
def drawer():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(frame=frame, code="A", column=1, row=1)
    return Drawer.objects.create(cabinet=cabinet, code="D-042", column=1, row=1)


@pytest.fixture
def component():
    category = Category.objects.create(name="Resistors", unit="Ω")
    return Component.objects.create(value="10k", category=category)


@pytest.mark.django_db
def test_component_detail_shows_its_drawer(client, component, drawer):
    Inventory.objects.create(component=component, drawer=drawer, quantity=7)

    response = client.get(reverse("components:component_detail", kwargs={"pk": component.pk}))

    assert response.status_code == 200
    assert b"D-042" in response.content
    assert b'value="7"' in response.content


@pytest.mark.django_db
def test_drawer_detail_shows_its_components(client, component, drawer):
    Inventory.objects.create(component=component, drawer=drawer, quantity=7)

    response = client.get(reverse("storage:drawer_detail", kwargs={"pk": drawer.pk}))

    assert response.status_code == 200
    assert "10k Ω".encode() in response.content
    assert b'value="7"' in response.content


@pytest.mark.django_db
def test_inventory_add_creates_stock_entry(client, component, drawer):
    response = client.post(
        reverse("inventory:inventory_add"),
        {"component": component.pk, "drawer": drawer.pk, "quantity": 12},
    )

    assert response.status_code == 302
    assert Inventory.objects.filter(component=component, drawer=drawer, quantity=12).exists()


@pytest.mark.django_db
def test_quantity_update_endpoint_updates_and_rerenders_row(client, component, drawer):
    entry = Inventory.objects.create(component=component, drawer=drawer, quantity=7)

    response = client.post(
        reverse("inventory:inventory_quantity", kwargs={"pk": entry.pk}) + "?show=drawer",
        {"quantity": 20},
    )

    assert response.status_code == 200
    entry.refresh_from_db()
    assert entry.quantity == 20
    assert b'value="20"' in response.content


@pytest.mark.django_db
def test_quantity_update_rejects_negative_values(client, component, drawer):
    entry = Inventory.objects.create(component=component, drawer=drawer, quantity=7)

    response = client.post(
        reverse("inventory:inventory_quantity", kwargs={"pk": entry.pk}) + "?show=drawer",
        {"quantity": -5},
    )

    assert response.status_code == 200
    entry.refresh_from_db()
    assert entry.quantity == 7
