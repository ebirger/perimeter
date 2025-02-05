from django.contrib import admin
from .models import Device, GlobalSettings

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'ip_address', 'hostname', 'status', 'first_seen', 'last_seen')
    list_filter = ('status',)
    search_fields = ('mac_address', 'hostname')


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('enforcement_mode',)
