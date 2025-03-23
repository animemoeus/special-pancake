from django.contrib import admin
from django.http import HttpResponseRedirect

from modules.models import Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    change_form_template = "modules/admin_edit_form.html"

    list_display = (
        "name",
        "description",
        "created_at",
        "updated_at",
        "is_active",
        "is_upgradable",
    )
    readonly_fields = ("created_at", "updated_at", "is_upgradable", "is_active")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("name", "created_at")

    def response_change(self, request, obj):
        if "_install" in request.POST:
            self.handle_install(request, obj)
            return HttpResponseRedirect(".")

        if "_uninstall" in request.POST:
            self.handle_uninstall(request, obj)
            return HttpResponseRedirect(".")

        if "_upgrade" in request.POST:
            self.handle_upgrade(request, obj)
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def handle_install(self, request, obj, post_url_continue=None):
        try:
            obj.activate()
            self.message_user(request, f"Module '{obj.name}' activated successfully.")
        except Exception as e:  # noqa: BLE001
            self.message_user(request, f"Error activating module: {e}", level="ERROR")

    def handle_uninstall(self, request, obj):
        try:
            obj.deactivate()
            self.message_user(request, f"Module '{obj.name}' deactivated successfully.")
        except Exception as e:  # noqa: BLE001
            self.message_user(request, f"Error deactivating module: {e}", level="ERROR")

    def handle_upgrade(self, request, obj):
        try:
            obj.upgrade()
            self.message_user(request, f"Module '{obj.name}' upgraded successfully.")
        except Exception as e:  # noqa: BLE001
            self.message_user(request, f"Error upgrading module: {e}", level="ERROR")
