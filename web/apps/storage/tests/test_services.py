import pytest

from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem
from apps.storage.services import (
    EMPTY_FRAME_SIZE,
    column_label,
    frame_bounding_box,
    generate_drawers_for_cabinet,
)


@pytest.mark.parametrize(
    "n,expected",
    [
        (1, "A"),
        (2, "B"),
        (26, "Z"),
        (27, "AA"),
        (28, "AB"),
        (52, "AZ"),
        (53, "BA"),
    ],
)
def test_column_label(n, expected):
    assert column_label(n) == expected


@pytest.mark.django_db
def test_generate_drawers_for_cabinet_creates_full_grid_with_expected_codes():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(frame=frame, code="A", column=2, row=3)

    generate_drawers_for_cabinet(cabinet)

    drawers = {d.code: (d.column, d.row) for d in Drawer.objects.filter(cabinet=cabinet)}
    assert drawers == {
        "A1": (1, 1),
        "A2": (1, 2),
        "A3": (1, 3),
        "B1": (2, 1),
        "B2": (2, 2),
        "B3": (2, 3),
    }


@pytest.mark.django_db
def test_generate_drawers_for_cabinet_creates_exactly_column_times_row_drawers():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(frame=frame, code="A", column=4, row=5)

    generate_drawers_for_cabinet(cabinet)

    assert Drawer.objects.filter(cabinet=cabinet).count() == 20


@pytest.mark.django_db
def test_frame_bounding_box_defaults_when_no_cabinets():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    assert frame_bounding_box(frame) == EMPTY_FRAME_SIZE


@pytest.mark.django_db
def test_frame_bounding_box_spans_all_cabinets():
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    Cabinet.objects.create(
        frame=frame, code="A", column=1, row=1,
        width=300, height=400, depth=250, position_x=0, position_y=0, position_z=0,
    )
    Cabinet.objects.create(
        frame=frame, code="B", column=1, row=1,
        width=300, height=400, depth=250, position_x=400, position_y=0, position_z=0,
    )

    box = frame_bounding_box(frame)

    assert box == {"width": 700, "height": 400, "depth": 250}
