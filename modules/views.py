from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from modules.models import Module


@login_required(login_url="/admin/login/")
@user_passes_test(lambda u: u.is_superuser)
def index(request):
    return HttpResponse("Module index page")


class ModuleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Module
    template_name = "modules/module_list.html"
    context_object_name = "modules"
    login_url = "/admin/login/"  # Uses Django admin login
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("Only superusers can access module management")


class ModuleActionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View to handle module actions: activate, deactivate, upgrade"""

    login_url = "/admin/login/"  # Uses Django admin login
    redirect_field_name = "next"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponse("Only superusers can access module management")

    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id)
        action = request.POST.get("action")

        try:
            if action == "activate":
                module.activate()
                messages.success(
                    request,
                    f"Module '{module.name}' activated successfully.",
                )
            elif action == "deactivate":
                module.deactivate()
                messages.success(
                    request,
                    f"Module '{module.name}' deactivated successfully.",
                )
            elif action == "upgrade":
                module.upgrade()
                messages.success(
                    request,
                    f"Module '{module.name}' upgraded successfully.",
                )
            else:
                messages.error(request, f"Unknown action: {action}")
        except Exception as e:  # noqa: BLE001
            messages.error(request, f"Error performing {action}: {e!s}")

        return HttpResponseRedirect(reverse("modules:module-list"))
