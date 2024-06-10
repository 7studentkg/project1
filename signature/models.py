from django.db import models
from workers.models import Client
from django.urls import reverse


class Signature(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='signature_client')
    title = models.TextField()
    sign_image = models.ImageField(upload_to='signatures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    signature_date = models.DateTimeField(null=True, blank=True)
    signed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('client-signature', kwargs={'signature_id': self.id})
