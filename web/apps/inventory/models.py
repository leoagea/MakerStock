from django.db import models


class Inventory(models.Model):
    component = models.ForeignKey(
        "components.Component", on_delete=models.CASCADE, related_name="stock_entries"
    )
    drawer = models.ForeignKey(
        "storage.Drawer", on_delete=models.CASCADE, related_name="stock_entries"
    )
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("component", "drawer")
        ordering = ["component"]
        verbose_name_plural = "inventory"

    def __str__(self):
        return f"{self.component} in {self.drawer}"

    @property
    def is_low_stock(self) -> bool:
        return self.low_stock_threshold is not None and self.quantity <= self.low_stock_threshold
