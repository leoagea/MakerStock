from django import forms

from .models import Component


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
