from import_export import resources
from .models import Giveaway, Platform, Supplier


class GiveawayResource(resources.ModelResource):
    class Meta:
        model = Giveaway


class PlatformResource(resources.ModelResource):
    class Meta:
        model = Platform


class SupplierResource(resources.ModelResource):
    class Meta:
        model = Supplier
