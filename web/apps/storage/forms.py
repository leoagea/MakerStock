from django import forms

from .models import Cabinet, Frame


class FrameForm(forms.ModelForm):
    class Meta:
        model = Frame
        fields = ["system", "code", "name"]


class CabinetForm(forms.ModelForm):
    class Meta:
        model = Cabinet
        fields = ["frame", "code", "name"]
