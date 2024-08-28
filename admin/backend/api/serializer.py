# api/serializers.py

from rest_framework import serializers
from .models import LectureMaterial

class LectureMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureMaterial
        fields = ['id', 'file', 'file_name', 'file_type', 'uploaded_at']
