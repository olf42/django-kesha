from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from kesha.models import Entry, ModelDoneError
from djmoney.money import Money
from kesha.tests.factories import (
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
            text="Testbuchung",
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
        e.text = e.text + "update"
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
            text="Testbuchung",
            virtual=True,
        )
        self.assertEquals(b.debit, Decimal("100.00"))
        self.assertEquals(b.credit, Decimal("100.00"))
