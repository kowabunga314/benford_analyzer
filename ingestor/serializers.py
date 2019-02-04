from rest_framework import serializers
from ingestor.config import SUPPORTED_SEPARATORS
from .models import BenfordRequest, Ingestor


class BenfordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = BenfordRequest
        fields = '__all__'  # ['column', 'separator']


class IngestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingestor
        fields = '__all__'
