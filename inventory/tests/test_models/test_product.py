import pytest
from django.db.utils import IntegrityError

from core.users.tests.factories import UserFactory
from inventory.models import Product
from inventory.models import StockLedgerEntry
from inventory.tests.factories import ProductFactory


@pytest.mark.django_db
class TestProductModel:
    """Test suite for the Product model."""

    def test_product_creation(self):
        """Test basic product creation."""
        user = UserFactory()
        product = ProductFactory(created_by=user, updated_by=user)
        assert Product.objects.count() == 1
        assert product.stock == 0
        assert product.created_by == user
        assert product.updated_by == user

    def test_product_str_representation(self):
        """Test the string representation of a product."""
        product = ProductFactory(name="Test Product")
        assert str(product) == "Test Product"

    def test_unique_barcode_constraint(self):
        """Test that product barcodes must be unique."""
        ProductFactory(barcode="12345678")

        with pytest.raises(IntegrityError):  # noqa: PT012
            product = ProductFactory(barcode="12345678")
            product.save()

    def test_get_stock_method(self):
        """Test the get_stock method calculates correctly from ledger entries."""
        product = ProductFactory()
        user = UserFactory()

        # Create some stock entries
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=10,
            created_by=user,
        )
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
            quantity=3,
            created_by=user,
        )

        # The stock should be calculated as 10-3=7
        assert product.get_stock() == 7  # noqa: PLR2004

    def test_reconcile_stock_method(self):
        """Test the reconcile_stock method updates the stock field correctly."""
        product = ProductFactory()
        user = UserFactory()

        # Create some stock entries
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=15,
            created_by=user,
        )
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
            quantity=5,
            created_by=user,
        )

        # Before reconciliation, stock might not match ledger
        product.stock = 0
        product.save()

        # Reconcile and check
        product.reconcile_stock()
        product.refresh_from_db()
        assert product.stock == 10  # noqa: PLR2004

    def test_stock_calculation_after_ledger_entry(self):
        """Test stock is updated after ledger entries are saved."""
        product = ProductFactory()
        user = UserFactory()
        assert product.stock == 0

        # Add stock
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=20,
            created_by=user,
        )

        # Refresh to get updated stock
        product.refresh_from_db()
        assert product.stock == 20  # noqa: PLR2004
