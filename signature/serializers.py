from rest_framework import serializers
from .models import Signature, Client

class SignatureSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Signature
        fields = ['id', 'client', 'client_name', 'file', 'sign_image', 'created_at', 'signature_date', 'signed']
        read_only_fields = ['id', 'created_at', 'signature_date', 'signed']

    def get_file(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("file обязательно поле для заполнения!")
        return value

    def create(self, validated_data):
        return Signature.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.file = validated_data.get('file', instance.file)
        instance.save()
        return instance
