from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.users.models import User


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_products",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_products",
    )

    def __str__(self):
        return f"{self.name}"

    def get_stock(self):
        """
        Calculate the total stock quantity for this product.
        Returns:
            int: The sum of all quantities in StockLedgerEntry objects related to this product.
                 Returns 0 if no entries are found or if the sum is None.
        """  # noqa: E501
        stock = StockLedgerEntry.objects.filter(product=self).aggregate(
            total_stock=Sum("quantity"),
        )["total_stock"]
        return stock or 0

    def reconcile_stock(self):
        """
        Reconciles the current stock value with the actual stock calculated from inventory.
        This method compares the current stock attribute with the actual stock
        calculated using the get_stock() method. If there's a discrepancy, it updates
        the stock value to match the actual count and saves the changes.
        Returns:
            bool: True if reconciliation was performed (stock was updated),
                  False if no update was needed (stocks already matched).
        """  # noqa: E501
        actual_stock = self.get_stock()
        if self.stock != actual_stock:
            self.stock = actual_stock
            self.save(update_fields=["stock"])
            return True
        return False


class StockLedgerEntry(models.Model):
    TRANSACTION_TYPE_IN = "IN"
    TRANSACTION_TYPE_OUT = "OUT"
    TRANSACTION_TYPE_ADJ = "ADJ"
    TRANSACTION_TYPES = [
        (TRANSACTION_TYPE_IN, "Stock In"),
        (TRANSACTION_TYPE_OUT, "Stock Out"),
        (TRANSACTION_TYPE_ADJ, "Stock Adjustment"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Stock Ledger Entry"
        verbose_name_plural = "Stock Ledger Entries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.full_clean()
            self._process_transaction()

        with transaction.atomic():
            super().save(*args, **kwargs)

    def clean(self):
        """
        Validate the model data based on transaction type.
        For IN transactions:
        - Validates that the quantity is positive
        For OUT transactions:
        - Validates that the quantity is positive
        - Checks if there is enough stock available
        Raises:
            ValidationError: If quantity is not positive or if there's insufficient stock for OUT transactions
        """  # noqa: E501
        super().clean()

        if self.transaction_type == self.TRANSACTION_TYPE_IN:
            if self.quantity <= 0:
                msg = "Quantity for IN transaction must be positive"
                raise ValidationError(msg)

        elif self.transaction_type == self.TRANSACTION_TYPE_OUT:
            if self.quantity <= 0:
                msg = "Quantity for OUT transaction must be positive"
                raise ValidationError(msg)

            product = Product.objects.select_for_update().get(pk=self.product.pk)
            if product.stock < self.quantity:
                msg = "Not enough stock available"
                raise ValidationError(msg)

    def _process_transaction(self):
        """
        Process the transaction based on its type.
        For OUT transactions:
        - Converts the quantity to negative for stock reduction
        """
        if self.transaction_type == self.TRANSACTION_TYPE_OUT:
            self.quantity = -self.quantity


@receiver(post_save, sender=StockLedgerEntry)
def update_product_stock(sender, instance, **kwargs):
    """
    Signal handler that updates a product's stock based on its StockLedgerEntry records.
    """
    product = instance.product

    # Recalculate from ledger entries
    updated_stock = (
        StockLedgerEntry.objects.filter(product=product).aggregate(
            total=Sum("quantity"),
        )["total"]
        or 0
    )

    # Save without triggering other signals
    Product.objects.filter(pk=product.pk).update(stock=updated_stock)
