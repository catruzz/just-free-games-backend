from .models import Giveaway, Platform, Supplier
from backend.resources import GiveawayResource, PlatformResource, SupplierResource
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


class GiveawayAdmin(ImportExportModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    resource_class = GiveawayResource


class PlatformAdmin(ImportExportModelAdmin):
    resource_class = PlatformResource


class SupplierAdmin(ImportExportModelAdmin):
    resource_class = SupplierResource


admin.site.register(Giveaway, GiveawayAdmin)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(Supplier, SupplierAdmin)
