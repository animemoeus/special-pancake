from django.contrib import admin

from modules.models import Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at", "is_active")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("name", "created_at")
