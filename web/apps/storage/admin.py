from django.contrib import admin

from .models import Cabinet, Drawer, StorageSystem


class CabinetInline(admin.TabularInline):
    model = Cabinet
    extra = 0


class DrawerInline(admin.TabularInline):
    model = Drawer
    extra = 0


@admin.register(StorageSystem)
class StorageSystemAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = [CabinetInline]


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ("code", "system")
    list_filter = ("system",)
    inlines = [DrawerInline]


@admin.register(Drawer)
class DrawerAdmin(admin.ModelAdmin):
    list_display = ("code", "cabinet")
    list_filter = ("cabinet__system", "cabinet")
