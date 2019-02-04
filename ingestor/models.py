from math import floor, log10
from django.db import models
from rest_framework.compat import MinValueValidator
from ingestor.config import SEP_CHOICES


class BenfordRequest(models.Model):
    column = models.IntegerField(null=False, blank=False)
    separator = models.CharField(null=False, blank=False, max_length=12, choices=SEP_CHOICES)
    file = models.FileField()


class Ingestor(models.Model):
    value = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
    msd = models.IntegerField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.msd = self.get_msd(self.value)
        super().save()

    @staticmethod
    def get_msd(num):
        return num // (10 ** floor(log10(num)))
