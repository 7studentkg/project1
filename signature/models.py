from django.db import models
from workers.models import Client
import uuid
from django.urls import reverse

class Signature(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='signature_client')
    title = models.TextField()
    image = models.ImageField(upload_to='signatures/', blank=True, null=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Добавлено поле UUID
    created_at = models.DateTimeField(auto_now_add=True)
    signature_date = models.DateTimeField(null=True, blank=True)
    signed = models.BooleanField(default=False)



    def get_absolute_url(self):
        return reverse('sing_api_view', kwargs={'unique_id': self.unique_id})
