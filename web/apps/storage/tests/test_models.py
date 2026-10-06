import pytest
from django.db import IntegrityError

from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem


@pytest.mark.django_db
def test_full_path_resolves_through_hierarchy():
    system = StorageSystem.objects.create(name="Workshop")
    cabinet = Cabinet.objects.create(system=system, code="A")
    frame = Frame.objects.create(cabinet=cabinet, code="4")
    drawer = Drawer.objects.create(frame=frame, code="D-042")

    assert cabinet.full_path == "Cabinet A"
    assert frame.full_path == "Frame 4 → Cabinet A"
    assert drawer.full_path == "Drawer D-042 → Frame 4 → Cabinet A"


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
