from django.core.validators import MinValueValidator
from django.db import models


class StorageSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Frame(models.Model):
    system = models.ForeignKey(StorageSystem, on_delete=models.CASCADE, related_name="frames")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("system", "code")
        ordering = ["code"]

    def __str__(self):
        return f"Frame {self.code}"

    @property
    def full_path(self) -> str:
        return f"Frame {self.code} → {self.system.name}"

class Cabinet(models.Model):
    """
    3D visualizer coordinate system (millimeters throughout):
      X = right, Y = up, Z = depth (into the frame, away from the viewer).
      Origin is the Frame's own bottom-left-front corner.
      position_x/y/z is this cabinet's minimum corner (bottom-left-front),
      not its center.
    """

    frame = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="cabinets")
    column = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    row = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)

    width = models.FloatField(default=300.0, validators=[MinValueValidator(1)])
    height = models.FloatField(default=400.0, validators=[MinValueValidator(1)])
    depth = models.FloatField(default=250.0, validators=[MinValueValidator(1)])
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    position_z = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("frame", "code")
        ordering = ["code"]

    def __str__(self):
        return f"Cabinet {self.code}"

    @property
    def full_path(self) -> str:
        return f"Cabinet {self.code} → {self.frame.full_path}"


class Drawer(models.Model):
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name="drawers")
    column = models.PositiveIntegerField()
    row = models.PositiveIntegerField()
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
