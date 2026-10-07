from django import forms

from .models import Category, Component, Manufacturer


class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = [
            "value",
            "category",
            "manufacturer",
            "manufacturer_part_number",
            "description",
            "datasheet_url",
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "unit", "parent"]


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ["name", "website"]
