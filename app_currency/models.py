from django.db import models
from django.utils import timezone


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    @property
    def timestamp_readable(self):
        """Более удобный формат даты и времени с учетом часового пояса"""
        local_time = timezone.localtime(self.timestamp)
        return local_time.strftime("%d.%m.%Y %H:%M:%S")

    def to_dict(self):
        """Сериализация в словарь"""
        return {
            "rate": str(self.rate),
            "currency": self.currency,
            "timestamp": self.timestamp_readable,
        }
