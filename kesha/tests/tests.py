from django.test import TestCase
from kesha.models import Booking, Entry, Account, Parent, ModelDoneError
from djmoney.money import Money


class KeshaCreateCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        p = Parent.objects.create(name="Bank Accounts", active=True)
        a = Account.objects.create(name="Bank Account 1", parent=p)
        b = Booking.objects.create()
        Entry.objects.create(
            account=a,
            booking=b,
            debit=Money(0.00, "EUR"),
            credit=Money(100.00, "EUR"),
            text="Testbuchung",
        )

    def test_booking_done(self):
        """Tests if a booking can be marked as done, but then not unmarked afterwards."""
        b = Booking.objects.get()
        b.done = True
        b.save()
        b.done = False
        self.assertRaises(ModelDoneError, b.save)
