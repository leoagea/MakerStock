import pytest
from django.urls import reverse

from apps.components.models import Category, Manufacturer


@pytest.mark.django_db
def test_catalog_admin_lists_categories_and_manufacturers(client):
    Category.objects.create(name="Resistors", unit="Ω")
    Manufacturer.objects.create(name="Yageo")

    response = client.get(reverse("components:catalog_admin"))

    assert response.status_code == 200
    assert b"Resistors" in response.content
    assert b"Yageo" in response.content


@pytest.mark.django_db
def test_catalog_admin_creates_category(client):
    response = client.post(
        reverse("components:catalog_admin"),
        {"action": "add_category", "name": "Capacitors", "unit": "F"},
    )

    assert response.status_code == 302
    assert Category.objects.filter(name="Capacitors", unit="F").exists()


@pytest.mark.django_db
def test_catalog_admin_creates_manufacturer(client):
    response = client.post(
        reverse("components:catalog_admin"),
        {"action": "add_manufacturer", "name": "Yageo", "website": "https://yageo.com"},
    )

    assert response.status_code == 302
    assert Manufacturer.objects.filter(name="Yageo").exists()


@pytest.mark.django_db
def test_catalog_admin_rejects_duplicate_category_name(client):
    Category.objects.create(name="Resistors", unit="Ω")

    response = client.post(
        reverse("components:catalog_admin"),
        {"action": "add_category", "name": "Resistors", "unit": "Ω"},
    )

    assert response.status_code == 200
    assert Category.objects.filter(name="Resistors").count() == 1
    assert b"already exists" in response.content


@pytest.mark.django_db
def test_category_edit_updates_category(client):
    category = Category.objects.create(name="Resistors", unit="Ω")

    response = client.post(
        reverse("components:category_edit", kwargs={"pk": category.pk}),
        {"name": "Resistors", "unit": "kΩ"},
    )

    assert response.status_code == 302
    category.refresh_from_db()
    assert category.unit == "kΩ"


@pytest.mark.django_db
def test_manufacturer_edit_updates_manufacturer(client):
    manufacturer = Manufacturer.objects.create(name="Yageo")

    response = client.post(
        reverse("components:manufacturer_edit", kwargs={"pk": manufacturer.pk}),
        {"name": "Yageo", "website": "https://yageo.com"},
    )

    assert response.status_code == 302
    manufacturer.refresh_from_db()
    assert manufacturer.website == "https://yageo.com"
