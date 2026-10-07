import pytest
from django.db import IntegrityError

from apps.storage.models import Cabinet, Drawer, StorageSystem


@pytest.mark.django_db
def test_full_path_resolves_through_hierarchy():
    system = StorageSystem.objects.create(name="Workshop")
    cabinet = Cabinet.objects.create(system=system, code="A")
    drawer = Drawer.objects.create(cabinet=cabinet, code="D-042")

    assert cabinet.full_path == "Cabinet A"
    assert drawer.full_path == "Drawer D-042 → Cabinet A"


@pytest.mark.django_db
def test_cabinet_code_unique_per_system():
    system = StorageSystem.objects.create(name="Workshop")
    Cabinet.objects.create(system=system, code="A")

    with pytest.raises(IntegrityError):
        Cabinet.objects.create(system=system, code="A")


@pytest.mark.django_db
def test_same_code_allowed_across_different_systems():
    system_one = StorageSystem.objects.create(name="Workshop")
    system_two = StorageSystem.objects.create(name="Garage")

    Cabinet.objects.create(system=system_one, code="A")
    # Should not raise: uniqueness is scoped per system, not global.
    Cabinet.objects.create(system=system_two, code="A")
