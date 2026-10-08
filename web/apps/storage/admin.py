from django.contrib import admin

from .models import Cabinet, Drawer, Frame, StorageSystem


class CabinetInline(admin.TabularInline):
    model = Cabinet
    extra = 0


class DrawerInline(admin.TabularInline):
    model = Drawer
    extra = 0

class FrameInline(admin.TabularInline):
    model = Frame
    extra = 0

@admin.register(StorageSystem)
class StorageSystemAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [FrameInline]

@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    list_display = ("code", "system")
    list_filter = ("system",)
    inlines = [CabinetInline]

@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ("code", "frame")
    list_filter = ("frame__system", "frame")
    inlines = [DrawerInline]


@admin.register(Drawer)
class DrawerAdmin(admin.ModelAdmin):
    list_display = ("code", "cabinet")
    list_filter = ("cabinet__frame__system", "cabinet")
    search_fields = ("code",)
