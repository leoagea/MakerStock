from django import forms

from .models import Cabinet, Frame


class FrameForm(forms.ModelForm):
    class Meta:
        model = Frame
        fields = ["system", "code", "name"]


class CabinetForm(forms.ModelForm):
    class Meta:
        model = Cabinet
        fields = [
            "frame",
            "code",
            "name",
            "column",
            "row",
            "width",
            "height",
            "depth",
        ]
        labels = {
            "column": "Number of columns",
            "row": "Number of rows",
            "width": "Width (mm)",
            "height": "Height (mm)",
            "depth": "Depth (mm)",
        }
        help_texts = {
            "column": "Drawers are created automatically from this grid, coded A1, A2, B1, …",
            "row": "Drawers are created automatically from this grid, coded A1, A2, B1, …",
        }
