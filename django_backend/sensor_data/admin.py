from django.contrib import admin
from .models import RawSensorData, EnrichedSensorData, HubConfig

@admin.register(RawSensorData)
class RawSensorDataAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'sensor_name', 'device_addr', 'sensor_val', 'datetime', 'sensor_id')

@admin.register(EnrichedSensorData)
class EnrichedSensorDataAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'sensor_name', 'device_addr', 'sensor_val', 'datetime', 'location', 'owner', 'workers')

@admin.register(HubConfig)
class HubConfigAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'location', 'owner', 'workers')
    readonly_fields = ('hub_id',)
    fields = ('hub_id', 'location', 'owner', 'workers')
