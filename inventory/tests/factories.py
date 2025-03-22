from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from core.users.tests.factories import UserFactory
from inventory.models import Product


class ProductFactory(DjangoModelFactory):
    """Factory for creating Product instances for testing."""

    name = Faker("sentence", nb_words=3)
    barcode = Faker("ean")
    price = Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=1,
    )

    # We don't set stock directly as it's calculated through StockLedgerEntry
    # or use the default value of 0

    created_by = SubFactory(UserFactory)
    updated_by = SubFactory(UserFactory)

    class Meta:
        model = Product
        django_get_or_create = ["name"]
