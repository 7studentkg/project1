from rest_framework import serializers
from .models import Signature

class SignatureSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Signature
        fields = ['id', 'client_id', 'title', 'unique_id', 'signed', 'absolute_url']

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
