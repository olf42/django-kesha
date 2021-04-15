from decimal import Decimal
from django.db.utils import IntegrityError
from django.test import TestCase
from kesha.models import Booking, Entry, Account, Parent, ModelDoneError
from djmoney.money import Money


class KeshaCreateCase(TestCase):
    def setUp(self):
        self.p = Parent.objects.create(name="Bank Accounts", active=True)
        self.a = Account.objects.create(name="Bank Account 1", parent=self.p)
        self.b = Booking.objects.create()
        self.e = Entry.objects.create(
            account=self.a,
            booking=self.b,
            debit=Money(100.00, "EUR"),
            text="Testbuchung",
        )

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

    def test_entry_of_done_booking_not_editable(self):
        """Tests if entries of a booking, which is marked as done, can be changed."""
        self.b.done = True
        self.b.save()
        self.e.text = "Testbuchung2"
        self.assertRaises(ModelDoneError, self.e.save)

    def test_booking_sum(self):
        a2 = Account.objects.create(name="Bank Account 2", parent=self.p)
        a3 = Account.objects.create(name="Bank Account 3", parent=self.p)
        b2 = Booking.objects.create()
        Entry.objects.create(
            account=a2,
            booking=self.b,
            credit=Money(123.45, "EUR"),
            text="Testbuchung",
        )
        Entry.objects.create(
            account=a3,
            booking=self.b,
            debit=Money(123.45, "EUR"),
            text="Testbuchung",
            virtual=True,
        )
        Entry.objects.create(
            account=a3,
            booking=b2,
            credit=Money(100.00, "EUR"),
            text="Testbuchung",
            virtual=True,
        )
        self.assertEquals(self.b.debit, Decimal("100.00"))
        self.assertEquals(self.b.credit, Decimal("123.45"))
        self.assertEquals(b2.debit, 0)
        self.assertEquals(b2.credit, 0)
