from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from modules.models import Module


def index(request):
    return HttpResponse("Module index page")


class ModuleListView(ListView):
    model = Module
    template_name = "modules/module_list.html"
    context_object_name = "modules"


class ModuleActionView(View):
    """View to handle module actions: activate, deactivate, upgrade"""

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
