from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=10)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subcategories"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Component(models.Model):
    value = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="components")
    manufacturer = models.ForeignKey(
        Manufacturer, null=True, blank=True, on_delete=models.SET_NULL, related_name="components"
    )
    manufacturer_part_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    datasheet_url = models.URLField(blank=True)
    specs = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["value"]

    def __str__(self):
        return self.display_name

    @property
    def display_name(self) -> str:
        if self.category.unit:
            return f"{self.value} {self.category.unit}"
        return self.value
