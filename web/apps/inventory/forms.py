from django import forms

from .models import Inventory


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["component", "drawer", "quantity", "low_stock_threshold"]
