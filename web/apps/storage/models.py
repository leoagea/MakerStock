from django.db import models


class StorageSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cabinet(models.Model):
    system = models.ForeignKey(StorageSystem, on_delete=models.CASCADE, related_name="cabinets")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("system", "code")
        ordering = ["code"]

    def __str__(self):
        return f"Cabinet {self.code}"

    @property
    def full_path(self) -> str:
        return f"Cabinet {self.code}"


class Drawer(models.Model):
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name="drawers")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("cabinet", "code")
        ordering = ["code"]

    def __str__(self):
        return f"Drawer {self.code}"

    @property
    def full_path(self) -> str:
        return f"Drawer {self.code} → {self.cabinet.full_path}"
