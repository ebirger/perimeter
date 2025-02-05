from django.db import models


class Device(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    hostname = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('allowed', 'Allowed'),
                 ('blocked', 'Blocked'),
                 ('pending', 'Pending')],
        default='pending'
    )
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mac_address} ({self.status})"


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class GlobalSettings(SingletonModel):
    enforcement_mode = models.CharField(
        max_length=30,
        choices=[('TRUST_AND_VERIFY', 'Trust and Verify'),
                 ('LOCK', 'Lock')],
        default='TRUST_AND_VERIFY'
    )
