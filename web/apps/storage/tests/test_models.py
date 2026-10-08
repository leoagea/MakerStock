import pytest
from django.db import IntegrityError

from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem


@pytest.mark.django_db
def test_full_path_resolves_through_hierarchy():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(frame=frame, code="A")
    drawer = Drawer.objects.create(cabinet=cabinet, code="D-042")

    assert frame.full_path == "Frame 4 → Workshop"
    assert cabinet.full_path == "Cabinet A → Frame 4 → Workshop"
    assert drawer.full_path == "Drawer D-042 → Cabinet A → Frame 4 → Workshop"


@pytest.mark.django_db
def test_frame_code_unique_per_system():
    system = StorageSystem.objects.create(name="Workshop")
    Frame.objects.create(system=system, code="4")

    with pytest.raises(IntegrityError):
        Frame.objects.create(system=system, code="4")


@pytest.mark.django_db
def test_cabinet_code_unique_per_frame():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    Cabinet.objects.create(frame=frame, code="A")

    with pytest.raises(IntegrityError):
        Cabinet.objects.create(frame=frame, code="A")


@pytest.mark.django_db
def test_same_cabinet_code_allowed_across_different_frames():
    system = StorageSystem.objects.create(name="Workshop")
    frame_one = Frame.objects.create(system=system, code="4")
    frame_two = Frame.objects.create(system=system, code="5")

    Cabinet.objects.create(frame=frame_one, code="A")
    # Should not raise: uniqueness is scoped per frame, not global.
    Cabinet.objects.create(frame=frame_two, code="A")
