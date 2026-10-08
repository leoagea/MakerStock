import pytest
from django.db import IntegrityError

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
def test_is_low_stock_true_when_quantity_at_or_below_threshold(component, drawer):
    entry = Inventory.objects.create(
        component=component, drawer=drawer, quantity=5, low_stock_threshold=5
    )
    assert entry.is_low_stock is True


@pytest.mark.django_db
def test_is_low_stock_false_when_no_threshold_set(component, drawer):
    entry = Inventory.objects.create(component=component, drawer=drawer, quantity=0)
    assert entry.is_low_stock is False


@pytest.mark.django_db
def test_component_cannot_be_stocked_twice_in_the_same_drawer(component, drawer):
    Inventory.objects.create(component=component, drawer=drawer, quantity=5)

    with pytest.raises(IntegrityError):
        Inventory.objects.create(component=component, drawer=drawer, quantity=3)
