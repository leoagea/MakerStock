import pytest
from django.urls import reverse

from apps.storage.models import Cabinet, Frame, StorageSystem


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


@pytest.mark.django_db
def test_cabinet_add_creates_cabinet(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.post(
        reverse("storage:cabinet_add"), {"frame": frame.pk, "code": "A", "name": ""}
    )

    assert response.status_code == 302
    assert Cabinet.objects.filter(frame=frame, code="A").exists()


@pytest.mark.django_db
def test_frame_detail_sidebar_context_reflects_current_frame(client):
    system = StorageSystem.objects.create(name="Workshop")
    frame = Frame.objects.create(system=system, code="4")

    response = client.get(reverse("storage:frame_detail", kwargs={"pk": frame.pk}))

    assert response.context["current_system"] == system
    assert response.context["current_frame"] == frame
    assert list(response.context["all_systems"]) == [system]
