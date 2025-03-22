from django.contrib import admin

from inventory.models import Product
from inventory.models import StockLedgerEntry


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "barcode",
        "price",
        "stock",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "barcode")
    ordering = ("-created_at",)
    readonly_fields = ("stock", "created_at", "updated_at", "created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StockLedgerEntry)
class StockLedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "transaction_type",
        "quantity",
        "created_at",
        "created_by",
    )
    list_filter = ("created_at",)
    search_fields = ("product__name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    exclude = ("created_by",)
    autocomplete_fields = ("product",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
