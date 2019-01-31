from django.db import models
from rest_framework.compat import MinValueValidator


class Ingestor(models.Model):
    value = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
