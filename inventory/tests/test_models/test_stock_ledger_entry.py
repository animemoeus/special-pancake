import pytest
from django.core.exceptions import ValidationError

from core.users.tests.factories import UserFactory
from inventory.models import StockLedgerEntry
from inventory.tests.factories import ProductFactory


@pytest.mark.django_db
class TestStockLedgerEntryModel:
    """Test suite for the StockLedgerEntry model."""

    def test_stock_ledger_entry_creation(self):
        """Test basic stock ledger entry creation."""
        product = ProductFactory()
        user = UserFactory()

        entry = StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=10,
            reference="Initial stock",
            created_by=user,
        )

        assert StockLedgerEntry.objects.count() == 1
        assert entry.product == product
        assert entry.transaction_type == "IN"
        assert entry.quantity == 10  # noqa: PLR2004
        assert entry.reference == "Initial stock"
        assert entry.created_by == user

    def test_stock_in_transaction(self):
        """Test stock in transactions add to product stock."""
        product = ProductFactory()
        user = UserFactory()

        # Initial stock should be zero
        assert product.stock == 0

        # Add stock
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=15,
            created_by=user,
        )

        # Refresh product from database
        product.refresh_from_db()
        assert product.stock == 15  # noqa: PLR2004

    def test_stock_out_transaction(self):
        """Test stock out transactions subtract from product stock."""
        product = ProductFactory()
        user = UserFactory()

        # Add initial stock
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=20,
            created_by=user,
        )

        product.refresh_from_db()
        assert product.stock == 20  # noqa: PLR2004

        # Remove some stock
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
            quantity=8,
            created_by=user,
        )

        product.refresh_from_db()
        assert product.stock == 12  # noqa: PLR2004

    def test_stock_adjustment_transaction(self):
        """Test stock adjustment transactions."""
        product = ProductFactory()
        user = UserFactory()

        # Add an adjustment entry
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_ADJ,
            quantity=5,  # Positive adjustment
            created_by=user,
        )

        product.refresh_from_db()
        assert product.stock == 5  # noqa: PLR2004

    def test_negative_stock_in_validation(self):
        """Test validation prevents negative quantities for stock in."""
        product = ProductFactory()
        user = UserFactory()

        with pytest.raises(ValidationError):  # noqa: PT012
            entry = StockLedgerEntry(
                product=product,
                transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
                quantity=-5,
                created_by=user,
            )
            entry.full_clean()

    def test_negative_stock_out_validation(self):
        """Test validation prevents negative quantities for stock out."""
        product = ProductFactory()
        user = UserFactory()

        with pytest.raises(ValidationError):  # noqa: PT012
            entry = StockLedgerEntry(
                product=product,
                transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
                quantity=-5,
                created_by=user,
            )
            entry.full_clean()

    def test_insufficient_stock_validation(self):
        """Test validation prevents stock out when there's not enough stock."""
        product = ProductFactory()
        user = UserFactory()

        # Initial stock = 0

        with pytest.raises(ValidationError):  # noqa: PT012
            entry = StockLedgerEntry(
                product=product,
                transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
                quantity=10,
                created_by=user,
            )
            entry.full_clean()

    def test_process_transaction_converts_out_quantity(self):
        """Test that _process_transaction converts OUT quantities to negative."""
        product = ProductFactory()
        user = UserFactory()

        # Add initial stock
        StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=20,
            created_by=user,
        )

        # The OUT transaction in the database should have negative quantity
        entry = StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_OUT,
            quantity=5,
            created_by=user,
        )

        # Get fresh instance from database
        entry.refresh_from_db()
        assert entry.quantity == -5  # Should be converted to negative  # noqa: PLR2004

    def test_string_representation(self):
        """Test the string representation of a stock ledger entry."""
        product = ProductFactory(name="Test Product")
        user = UserFactory()

        entry = StockLedgerEntry.objects.create(
            product=product,
            transaction_type=StockLedgerEntry.TRANSACTION_TYPE_IN,
            quantity=10,
            created_by=user,
        )

        assert str(entry) == "Test Product"
