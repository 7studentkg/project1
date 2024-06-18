from rest_framework import serializers
from .models import Signature, Client

class SignatureSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    sign_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Signature
        fields = ['id', 'client', 'client_name', 'file', 'file_url', 'sign_image', 'sign_image_url', 'created_at', 'signature_date', 'signed']
        read_only_fields = ['id', 'created_at', 'signature_date', 'signed']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_sign_image_url(self, obj):
        request = self.context.get('request')
        if obj.sign_image:
            return request.build_absolute_uri(obj.sign_image.url)
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
