from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect

from modules.models import Module


class InventoryModuleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Middleware call method to intercept requests.
        This method checks if a request is directed to the inventory module and verifies
        that the module is active and registered in the system before allowing the request
        to proceed. If the module is not active or does not exist, it redirects the user
        appropriately.
        Args:
            request (HttpRequest): The request object being processed.
        Returns:
            HttpResponse: Either a redirect response if the inventory module check fails,
                         or the response from the next middleware or view.
        Raises:
            Http404: If the inventory module exists but is not active.
        """  # noqa: E501

        # Check if the path starts with /inventory/
        if request.path.startswith("/inventory/"):
            try:
                module = Module.objects.get(name="inventory")
                if not module.is_active:
                    raise Http404
            except Module.DoesNotExist:
                messages.error(
                    request,
                    "The Inventory module is not registered in the system.",
                )
                return redirect("/")

        return self.get_response(request)
