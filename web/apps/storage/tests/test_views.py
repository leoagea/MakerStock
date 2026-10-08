import json

import pytest
from django.urls import reverse

from apps.components.models import Category, Component
from apps.inventory.models import Inventory
from apps.storage.models import Cabinet, Drawer, Frame, StorageSystem
from apps.storage.services import generate_drawers_for_cabinet


@pytest.mark.django_db
def test_frame_add_prefills_system_from_query_param(client):
    system = StorageSystem.objects.create(name="Workshop")

    response = client.get(reverse("storage:frame_add"), {"system": system.pk})

    assert response.status_code == 200
    assert response.context["form"].initial["system"] == str(system.pk)
    assert response.context["current_system"] == system


@pytest.mark.django_db
def test_frame_add_creates_frame(client):
    system = StorageSystem.objects.create(name="Workshop")

    response = client.post(
        reverse("storage:frame_add"), {"system": system.pk, "code": "4", "name": ""}
    )

    assert response.status_code == 302
    assert Frame.objects.filter(system=system, code="4").exists()


@pytest.mark.django_db
def test_cabinet_add_prefills_frame_from_query_param(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.get(reverse("storage:cabinet_add"), {"frame": frame.pk})

    assert response.status_code == 200
    assert response.context["form"].initial["frame"] == str(frame.pk)
    assert response.context["current_frame"] == frame
    assert response.context["current_system"] == system


CABINET_GEOMETRY = {
    "width": 300,
    "height": 400,
    "depth": 250,
    "position_x": 0,
    "position_y": 0,
    "position_z": 0,
}


@pytest.mark.django_db
def test_cabinet_add_creates_cabinet(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.post(
        reverse("storage:cabinet_add"),
        {"frame": frame.pk, "code": "A", "name": "", "column": 2, "row": 3, **CABINET_GEOMETRY},
    )

    assert response.status_code == 302
    assert Cabinet.objects.filter(frame=frame, code="A", column=2, row=3).exists()


@pytest.mark.django_db
def test_cabinet_add_generates_its_drawer_grid(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    client.post(
        reverse("storage:cabinet_add"),
        {"frame": frame.pk, "code": "A", "name": "", "column": 2, "row": 3, **CABINET_GEOMETRY},
    )

    cabinet = Cabinet.objects.get(frame=frame, code="A")
    codes = set(Drawer.objects.filter(cabinet=cabinet).values_list("code", flat=True))
    assert codes == {"A1", "A2", "A3", "B1", "B2", "B3"}


@pytest.mark.django_db
def test_frame_detail_sidebar_context_reflects_current_frame(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.get(reverse("storage:frame_detail", kwargs={"pk": frame.pk}))

    assert response.context["current_system"] == system
    assert response.context["current_frame"] == frame
    assert list(response.context["all_systems"]) == [system]


@pytest.mark.django_db
def test_frame_3d_page_renders(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.get(reverse("storage:frame_3d", kwargs={"pk": frame.pk}))

    assert response.status_code == 200
    assert response.context["current_frame"] == frame
    assert response.context["current_system"] == system


@pytest.mark.django_db
def test_frame_visualization_data_shape(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")
    cabinet = Cabinet.objects.create(
        frame=frame,
        code="A",
        column=2,
        row=1,
        width=300,
        height=400,
        depth=250,
        position_x=10,
        position_y=20,
        position_z=30,
    )
    generate_drawers_for_cabinet(cabinet)

    category = Category.objects.create(name="Resistors", unit="Ω")
    component = Component.objects.create(value="10k", category=category)
    drawer_a1 = Drawer.objects.get(cabinet=cabinet, code="A1")
    Inventory.objects.create(component=component, drawer=drawer_a1, quantity=5)

    response = client.get(reverse("storage:frame_visualization_data", kwargs={"pk": frame.pk}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["id"] == frame.pk
    assert data["code"] == "4"

    [cabinet_data] = data["cabinets"]
    assert cabinet_data["code"] == "A"
    assert cabinet_data["position"] == {"x": 10, "y": 20, "z": 30}
    assert cabinet_data["dimensions"] == {"width": 300, "height": 400, "depth": 250}
    assert cabinet_data["grid"] == {"columns": 2, "rows": 1}
    assert len(cabinet_data["drawers"]) == 2

    drawer_data = next(d for d in cabinet_data["drawers"] if d["code"] == "A1")
    assert drawer_data["column"] == 1
    assert drawer_data["row"] == 1
    assert drawer_data["component_count"] == 1

    other_drawer = next(d for d in cabinet_data["drawers"] if d["code"] != "A1")
    assert other_drawer["component_count"] == 0


@pytest.mark.django_db
def test_system_3d_page_renders(client):
    system = StorageSystem.objects.create(name="Workshop")

    response = client.get(reverse("storage:system_3d", kwargs={"pk": system.pk}))

    assert response.status_code == 200
    assert response.context["current_system"] == system


@pytest.mark.django_db
def test_system_visualization_data_shape(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame_with_cabinet = Frame.objects.create(system=system, code="4")
    Cabinet.objects.create(
        frame=frame_with_cabinet, code="A", column=1, row=1,
        width=300, height=400, depth=250, position_x=0, position_y=0, position_z=0,
    )
    empty_frame = Frame.objects.create(system=system, code="5")

    response = client.get(reverse("storage:system_visualization_data", kwargs={"pk": system.pk}))

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["id"] == system.pk

    by_code = {f["code"]: f for f in data["frames"]}
    assert by_code["4"]["cabinet_count"] == 1
    assert by_code["4"]["dimensions"] == {"width": 300, "height": 400, "depth": 250}
    assert by_code["4"]["url"] == reverse("storage:frame_3d", kwargs={"pk": frame_with_cabinet.pk})

    assert by_code["5"]["cabinet_count"] == 0
    assert by_code["5"]["url"] == reverse("storage:frame_3d", kwargs={"pk": empty_frame.pk})
