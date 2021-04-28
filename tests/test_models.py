from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from kesha.models import Entry, Parent, ModelDoneError
from djmoney.money import Money
from tests.factories import (
    ActiveParentFactory,
    ActiveAccountFactory,
    BookingFactory,
)


class KeshaTestCase(TestCase):
    def setUp(self):
        self.p = ActiveParentFactory()
        self.a = ActiveAccountFactory()
        self.b = BookingFactory(good=True)

    def test_entry(self):
        """Test if an entry can have both filled debit and credit (shouldn't be possible)."""
        e = Entry(
            account=self.a,
            booking=self.b,
            debit=Money(10.00, "EUR"),
            credit=Money(10.00, "EUR"),
        )
        self.assertRaises(IntegrityError, e.save)

    def test_booking_done(self):
        """Tests if a booking can be marked as done, but then not unmarked afterwards."""
        self.b.done = True
        self.b.save()
        self.b.done = False
        self.assertRaises(ModelDoneError, self.b.save)

    def test_booking_done_with_unequal_entries(self):
        b = BookingFactory()
        b.done = True
        self.assertRaises(ValidationError, b.save)

    def test_entry_of_done_booking_not_editable(self):
        """Tests if entries of a booking, which is marked as done, can be changed."""
        self.b.done = True
        self.b.save()
        e = self.b.entries.all()[0]
        print(e.credit)
        e.credit = Money(123.00, "EUR")
        self.assertRaises(ModelDoneError, e.save)

    def test_booking_sum(self):
        """
        Creates a good booking (i.e. the sum of the entries debit = sum of entries credit.
        Also virtual entries are not accounted for.
        """
        b = BookingFactory(good=True)
        Entry.objects.create(
            account=ActiveAccountFactory(),
            booking=b,
            credit=Money(100.00, "EUR"),
            virtual=True,
        )
        self.assertEqual(b.debit, Decimal("100.00"))
        self.assertEqual(b.credit, Decimal("100.00"))

    def test_account_sum(self):
        b = BookingFactory()
        self.assertEqual(b.entries.get().account.debit, Decimal("100"))

    def test_parent_sum(self):
        """
        The good booking self.b consist of two entries onto two different accounts.
        Both of which have different parents, and therefore the same sum on either
        debit or credit.
        """
        parent_1 = self.b.entries.all()[0].account.parent
        parent_2 = self.b.entries.all()[1].account.parent
        self.assertEqual(parent_1.debit, Decimal(100.0))
        self.assertEqual(parent_2.credit, Decimal(100.0))

    def test_parent_recurse(self):
        """Tests if sums from child parents are correctly displayed for the parents"""
        parent_1 = self.b.entries.all()[0].account.parent
        parent_2 = self.b.entries.all()[1].account.parent
        p1 = ActiveParentFactory()
        p2 = ActiveParentFactory()
        parent_1.parent = p1
        parent_1.save()
        parent_2.parent = p2
        parent_2.save()
        self.assertEqual(p1.debit, Decimal(100.0))
        self.assertEqual(p2.credit, Decimal(100.0))

    def test_get_roots(self):
        root_nodes = Parent.objects.get_roots()
        expectations = [
            {
                "name": "Active Parent 031",
                "debit": Decimal("0.0"),
                "credit": Decimal("0.0"),
            },
            {
                "name": "Active Parent 032",
                "debit": Decimal("0.0"),
                "credit": Decimal("0.0"),
            },
            {
                "name": "Active Parent 033",
                "debit": Decimal("100.0"),
                "credit": Decimal("0.0"),
            },
            {
                "name": "Active Parent 034",
                "debit": Decimal("0.0"),
                "credit": Decimal("100.0"),
            },
        ]
        for node, exp in zip(root_nodes, expectations):
            self.assertEqual(node.name, exp["name"])
            self.assertEqual(node.debit, exp["debit"])
            self.assertEqual(node.credit, exp["credit"])
