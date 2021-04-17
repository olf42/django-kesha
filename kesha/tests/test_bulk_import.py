import yaml

from djmoney.money import Money
from django.test import TestCase
from kesha.models import Booking
from kesha.tests.factories import ActiveParentFactory, ActiveAccountFactory
from pathlib import Path

ENTRIES_FILENAME = Path(__file__).parent / "entries.yaml"
CUR = "EUR"


def get_entries(entries_filename=ENTRIES_FILENAME):
    with open(entries_filename) as infile:
        return yaml.safe_load(infile)


class BulkImportTestCase(TestCase):
    def setUp(self):
        self.p = ActiveParentFactory()
        self.a = ActiveAccountFactory()

    def test_bulk_import(self):
        entries = get_entries()
        bookings = Booking.objects.bulk_import(entries, self.a)
        self.assertEqual(len(entries), len(bookings))
        for entry, booking in zip(entries, bookings):
            self.assertEqual(len(booking.entries.all()), 1)
            b_entry = booking.entries.get()
            self.assertEqual(entry["text"], b_entry.text)
            if "debit" in entry.keys():
                self.assertEqual(Money(entry["debit"], CUR), b_entry.debit)
            else:
                self.assertEqual(Money(entry["credit"], CUR), b_entry.credit)
