from rest_framework import serializers
from .models import Ingestor


class IngestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingestor
        fields = '__all__'
