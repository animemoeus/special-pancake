from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from inventory.models import Product


class ProductListView(ListView):
    model = Product
    template_name = "inventory/product_list.html"
    context_object_name = "products"
    paginate_by = 10  # Number of products per page

    def get_queryset(self):
        return Product.objects.all().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_user_role"] = (
            self.request.user.groups.filter(name="User").exists()
            or self.request.user.is_superuser
        )
        context["has_manager_role"] = (
            self.request.user.groups.filter(name="Manager").exists()
            or self.request.user.is_superuser
        )
        return context


class ProductCreateView(View):
    """View to handle product creation"""

    def post(self, request):
        try:
            product = Product(
                name=request.POST.get("name"),
                price=request.POST.get("price"),
                barcode=request.POST.get("barcode") or None,
                stock=int(request.POST.get("stock", 0)),
                created_by=request.user,
                updated_by=request.user,
            )
            product.save()
            messages.success(request, f"Product '{product.name}' created successfully.")
        except Exception as e:  # noqa: BLE001
            messages.error(request, f"Error creating product: {e}")

        return HttpResponseRedirect(reverse("inventory:product-list"))


class ProductUpdateView(View):
    """View to handle product updates"""

    def post(self, request, product_id):
        # Check if user has User or Manager permissions
        has_permission = (
            self.request.user.groups.filter(name__in=["User", "Manager"]).exists()
            or self.request.user.is_superuser
        )

        if not has_permission:
            messages.error(
                request,
                "Permission denied: Only users or managers can update products.",
            )
            return HttpResponseRedirect(reverse("inventory:product-list"))

        product = get_object_or_404(Product, id=product_id)

        # Update product fields
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.barcode = request.POST.get("barcode")
        product.stock = request.POST.get("stock")

        try:
            product.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
        except Exception as e:  # noqa: BLE001
            messages.error(request, f"Error updating product: {e}")

        return HttpResponseRedirect(reverse("inventory:product-list"))


class ProductDeleteView(View):
    """View to handle product deletion"""

    def post(self, request, product_id):
        # Check if user has Manager permissions
        has_manager_role = (
            self.request.user.groups.filter(name="Manager").exists()
            or self.request.user.is_superuser
        )

        if not has_manager_role:
            messages.error(
                request,
                "Permission denied: Only managers can delete products.",
            )
            return HttpResponseRedirect(reverse("inventory:product-list"))

        product = get_object_or_404(Product, id=product_id)
        product_name = product.name

        try:
            product.delete()
            messages.success(request, f"Product '{product_name}' deleted successfully.")
        except Exception as e:  # noqa: BLE001
            messages.error(request, f"Error deleting product: {e}")

        return HttpResponseRedirect(reverse("inventory:product-list"))
