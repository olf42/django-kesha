from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.text import slugify
from django.utils.translation import gettext as _
from djmoney.models.fields import MoneyField

MODEL_DONE_ERROR_MSG = _("Models marked as done can not be edited anymore.")


class ModelDoneError(Exception):
    def __init__(self, msg=MODEL_DONE_ERROR_MSG, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class CreatedModifiedModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class SlugifiedModel(models.Model):
    slug = models.SlugField(editable=False, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Parent(CreatedModifiedModel, SlugifiedModel):
    name = models.CharField(max_length=255)
    active = models.BooleanField()


class Account(CreatedModifiedModel, SlugifiedModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "Parent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="child_accounts",
    )
    virtual = models.BooleanField(default=False)

    class Meta:
        unique_together = [["name", "parent"]]

    @property
    def active(self):
        return self.parent.active


class Booking(CreatedModifiedModel):
    done = models.BooleanField(default=False)

    __done = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__done = self.done

    @property
    def debit(self):
        return self.get_entry_sum("debit")

    @property
    def credit(self):
        return self.get_entry_sum("credit")

    def get_entry_sum(self, column):
        value = Entry.objects.filter(booking=self, virtual=False).aggregate(
            Sum(column)
        )[f"{column}__sum"]
        return value if value is not None else Decimal(0.0)

    @property
    def entry_sums_match(self):
        return self.get_entry_sum("debit") == self.get_entry_sum("credit")

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.done and self.done == self.__done:
            raise ModelDoneError()
        elif self.done and self.done != self.__done:
            if not self.entry_sums_match:
                self.done = False
                raise ValidationError(
                    _(f"Entry sums do not match up Debit {self.debit} != {self.credit}")
                )
            else:
                super().save(force_insert, force_update, *args, **kwargs)
            self.__done = self.done
        elif not self.done and self.done == self.__done:
            super().save(force_insert, force_update, *args, **kwargs)
            self.__done = self.done
        elif not self.done and self.done != self.__done:
            raise ModelDoneError()


class Entry(CreatedModifiedModel):
    account = models.ForeignKey(
        "Account", on_delete=models.PROTECT, related_name="entries"
    )
    booking = models.ForeignKey(
        "Booking", on_delete=models.PROTECT, related_name="entries"
    )
    text = models.TextField()
    debit = MoneyField(
        max_digits=14, decimal_places=2, default_currency="EUR", null=True, blank=True
    )
    credit = MoneyField(
        max_digits=14, decimal_places=2, default_currency="EUR", null=True, blank=True
    )
    virtual = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_either_debit_or_credit",
                check=(
                    models.Q(debit__isnull=True, credit__isnull=False)
                    | models.Q(debit__isnull=False, credit__isnull=True)
                ),
            )
        ]

    def save(self, *args, **kwargs):
        if self.done:
            raise ModelDoneError()
        else:
            super().save(*args, **kwargs)

    @property
    def done(self):
        return self.booking.done
