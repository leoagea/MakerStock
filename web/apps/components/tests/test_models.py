import pytest
from django.db.models import ProtectedError

from apps.components.models import Category, Component, Manufacturer


@pytest.mark.django_db
def test_component_str_combines_value_and_category_unit():
    category = Category.objects.create(name="Resistors", unit="Ω")
    component = Component.objects.create(value="10k", category=category)
    assert str(component) == "10k Ω"
    assert component.display_name == "10k Ω"


@pytest.mark.django_db
def test_display_name_omits_unit_when_category_has_none():
    category = Category.objects.create(name="Misc")
    component = Component.objects.create(value="10k", category=category)
    assert component.display_name == "10k"


@pytest.mark.django_db
def test_category_cannot_be_deleted_while_in_use():
    category = Category.objects.create(name="Resistors", unit="Ω")
    Component.objects.create(value="10k", category=category)

    with pytest.raises(ProtectedError):
        category.delete()


@pytest.mark.django_db
def test_manufacturer_delete_sets_null_on_component():
    category = Category.objects.create(name="Resistors", unit="Ω")
    manufacturer = Manufacturer.objects.create(name="Yageo")
    component = Component.objects.create(
        value="10k", category=category, manufacturer=manufacturer
    )

    manufacturer.delete()
    component.refresh_from_db()
    assert component.manufacturer is None
