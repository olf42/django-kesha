from django.db import models
from django.utils.text import slugify
from djmoney.models.fields import MoneyField


class ModelDoneError(Exception):
    pass


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

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.done and self.done == self.__done:
            raise ModelDoneError("Models marked as done can not be edited anymore.")
        elif self.done and self.done != self.__done:
            super().save(force_insert, force_update, *args, **kwargs)
            self.__done = self.done
        elif not self.done and self.done == self.__done:
            super().save(force_insert, force_update, *args, **kwargs)
            self.__done = self.done
        elif not self.done and self.done != self.__done:
            raise ModelDoneError("Models marked as done can not be edited anymore.")


class Entry(CreatedModifiedModel):
    account = models.ForeignKey(
        "Account", on_delete=models.PROTECT, related_name="entries"
    )
    booking = models.ForeignKey(
        "Booking", on_delete=models.PROTECT, related_name="entries"
    )
    text = models.TextField()
    debit = MoneyField(max_digits=14, decimal_places=2, default_currency="EUR")
    credit = MoneyField(max_digits=14, decimal_places=2, default_currency="EUR")
    virtual = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.done:
            raise ModelDoneError("Models marked as done can not be edited anymore.")
        else:
            super().save(*args, **kwargs)

    @property
    def done(self):
        return self.booking.done
