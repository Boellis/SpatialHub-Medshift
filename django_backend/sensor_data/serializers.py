from rest_framework import serializers
from .models import *

class RawSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSensorData
        fields = '__all__'

class EnrichedSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrichedSensorData
        fields = '__all__'

class HubConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HubConfig
        fields = '__all__'
