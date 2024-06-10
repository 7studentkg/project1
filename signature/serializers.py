from rest_framework import serializers
from .models import Signature, Client

class SignatureSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Signature
        fields = ['id', 'client', 'client_name', 'title', 'sign_image', 'created_at', 'signature_date', 'signed']
        read_only_fields = ['id', 'created_at', 'signature_date', 'signed']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("title обязательно поле для заполнения!")
        return value

    def create(self, validated_data):
        return Signature.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance
