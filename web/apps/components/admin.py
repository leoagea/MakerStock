from django.contrib import admin

from .models import Category, Component, Manufacturer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "unit")
    list_filter = ("parent",)
    search_fields = ("name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("value", "category", "manufacturer", "manufacturer_part_number")
    list_filter = ("category", "manufacturer")
    search_fields = ("value", "manufacturer_part_number", "description")
