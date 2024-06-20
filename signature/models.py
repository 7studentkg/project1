from django.db import models
from workers.models import Client
from django.urls import reverse
import os

def get_signature_path(instance, filename):
    return f'signature/{instance.client.id}/{filename}'

def get_sign_image_path(instance, filename):
    base, ext = os.path.splitext(filename)
    new_filename = f'sign_{base}{ext}'

    return f'signature/{instance.client.id}/{new_filename}'

class Signature(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='signature_client')
    file = models.FileField(upload_to=get_signature_path, max_length=300)
    sign_image = models.ImageField(upload_to=get_sign_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    signature_date = models.DateTimeField(null=True, blank=True)
    signed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('signature-detail', kwargs={'client_id': self.client.id, 'signature_id': self.id})

    class Meta:
        verbose_name = "Подпись"
        verbose_name_plural = "Подписи"
