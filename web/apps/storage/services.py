from .models import Cabinet, Drawer, Frame

# Placeholder size (mm) for a frame with no cabinets yet, so it still renders
# as something visible/clickable in the system-level 3D overview.
EMPTY_FRAME_SIZE = {"width": 400.0, "height": 500.0, "depth": 300.0}


def frame_bounding_box(frame: Frame) -> dict:
    """The frame's footprint for the system-level 3D overview: the bounding
    box of all its cabinets' real positions/dimensions, in millimeters."""
    cabinets = list(frame.cabinets.all())
    if not cabinets:
        return dict(EMPTY_FRAME_SIZE)

    min_x = min(c.position_x for c in cabinets)
    min_y = min(c.position_y for c in cabinets)
    min_z = min(c.position_z for c in cabinets)
    max_x = max(c.position_x + c.width for c in cabinets)
    max_y = max(c.position_y + c.height for c in cabinets)
    max_z = max(c.position_z + c.depth for c in cabinets)

    return {
        "width": max_x - min_x,
        "height": max_y - min_y,
        "depth": max_z - min_z,
    }


def column_label(n: int) -> str:
    """Spreadsheet-style column label: 1 -> A, 2 -> B, ..., 26 -> Z, 27 -> AA, ..."""
    label = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        label = chr(65 + remainder) + label
    return label


def generate_drawers_for_cabinet(cabinet: Cabinet) -> list[Drawer]:
    """Creates the cabinet's full column x row grid of drawers, coded e.g. A1, A2, B1, B2."""
    drawers = [
        Drawer(cabinet=cabinet, column=column, row=row, code=f"{column_label(column)}{row}")
        for column in range(1, cabinet.column + 1)
        for row in range(1, cabinet.row + 1)
    ]
    return Drawer.objects.bulk_create(drawers)
