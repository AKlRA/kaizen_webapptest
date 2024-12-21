# kaizen_app/api/serializers.py
from rest_framework import serializers
from ..models import KaizenSheet, Profile

class KaizenSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = KaizenSheet
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile 
        fields = '__all__'