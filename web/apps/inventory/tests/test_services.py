import pytest

from apps.components.models import Category, Component
from apps.inventory.models import Inventory
from apps.inventory.services import low_stock_entries
from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem


@pytest.fixture
def drawer():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(frame=frame, code="A", column=1, row=1)
    return Drawer.objects.create(cabinet=cabinet, code="D-042", column=1, row=1)


@pytest.fixture
def category():
    return Category.objects.create(name="Resistors", unit="Ω")


@pytest.mark.django_db
def test_low_stock_entries_includes_entries_at_or_below_threshold(drawer, category):
    low = Component.objects.create(value="10k", category=category)
    Inventory.objects.create(component=low, drawer=drawer, quantity=3, low_stock_threshold=5)

    results = list(low_stock_entries())

    assert len(results) == 1
    assert results[0].component == low


@pytest.mark.django_db
def test_low_stock_entries_excludes_entries_above_threshold(drawer, category):
    fine = Component.objects.create(value="1k", category=category)
    Inventory.objects.create(component=fine, drawer=drawer, quantity=50, low_stock_threshold=5)

    assert list(low_stock_entries()) == []


@pytest.mark.django_db
def test_low_stock_entries_excludes_entries_without_threshold(drawer, category):
    untracked = Component.objects.create(value="100n", category=category)
    Inventory.objects.create(component=untracked, drawer=drawer, quantity=0, low_stock_threshold=None)

    assert list(low_stock_entries()) == []
