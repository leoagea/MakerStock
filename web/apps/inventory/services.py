from django.db.models import F, QuerySet

from .models import Inventory


def low_stock_entries() -> QuerySet[Inventory]:
    """Stock entries at or below their configured low-stock threshold."""
    return (
        Inventory.objects.filter(low_stock_threshold__isnull=False)
        .filter(quantity__lte=F("low_stock_threshold"))
        .select_related("component", "component__category", "drawer__cabinet")
        .order_by("component__value")
    )
