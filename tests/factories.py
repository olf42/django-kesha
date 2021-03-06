import factory
import factory.django
import random
import string

from kesha.models import Parent, Account, Booking, Entry
from djmoney.money import Money


class ActiveParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parent

    name = factory.Sequence(lambda n: f"Active Parent {n:03d}")
    active = True


class PassiveParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parent

    name = factory.Sequence(lambda n: f"Passive Parent {n:03d}")
    active = False


class ActiveAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f"Account {n:03d}")
    parent = factory.SubFactory(ActiveParentFactory)
    virtual = False


class PassiveActiveAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    name = factory.Sequence(lambda n: f"Account {n:03d}")
    parent = factory.SubFactory(PassiveParentFactory)
    virtual = False


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    account = factory.SubFactory(ActiveAccountFactory)
    virtual = False


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    text = "Booking Text".join(random.choices(string.ascii_letters, k=20))
    entry_1 = factory.RelatedFactory(
        EntryFactory, factory_related_name="booking", debit=Money("100.0", "EUR")
    )

    class Params:
        good = factory.Trait(
            entry_2=factory.RelatedFactory(
                EntryFactory,
                factory_related_name="booking",
                credit=Money("100.0", "EUR"),
            )
        )
