import uuid
from django.db import models

class BaseUUIDModel(models.Model):
    """
    Modelo base abstrato que utiliza UUIDv4 como chave primária.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(BaseUUIDModel):
    """
    Modelo base abstrato que adiciona campos de auditoria temporal.
    """
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
