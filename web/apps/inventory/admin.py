from django.contrib import admin

from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("component", "drawer", "quantity", "low_stock_threshold", "is_low_stock")
    list_filter = ("drawer__cabinet__frame__system",)
    autocomplete_fields = ("component", "drawer")
