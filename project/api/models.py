from django.db import models
from datetime import datetime
from django.utils.timezone import now

# Crypto Models ===========================================================>

class Coin(models.Model):
    name = models.CharField(max_length=200, blank=False, default='')
    symbol = models.CharField(max_length=20, blank=False, default='')
    open = models.DecimalField(max_digits=25, decimal_places=8)
    high = models.DecimalField(max_digits=25, decimal_places=8)
    low = models.DecimalField(max_digits=25, decimal_places=8)
    close = models.DecimalField(max_digits=25, decimal_places=8)
    volume = models.DecimalField(max_digits=25, decimal_places=8)
    last_update = models.DateTimeField()

    @property
    def LastRefresh(self):
        delta = now() - self.last_update
        return delta.seconds//60

class Key(models.Model):
    hash = models.CharField(max_length=255, blank=False, default='')
    expiry_date = models.DateTimeField()