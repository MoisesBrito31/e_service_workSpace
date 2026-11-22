import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modelo de Usuário customizado com UUID e perfis de atuação no sistema.
    """
    class CargoChoices(models.TextChoices):
        VENDEDOR = 'VENDEDOR', 'Vendedor'
        GESTOR = 'GESTOR', 'Gestor de Engenharia / Projetos'
        TECNICO = 'TECNICO', 'Técnico de Desenvolvimento'
        COMERCIAL = 'COMERCIAL', 'Equipe Comercial'
        ADMIN = 'ADMIN', 'Administrador'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cargo = models.CharField(
        'Cargo / Perfil',
        max_length=20,
        choices=CargoChoices.choices,
        default=CargoChoices.TECNICO,
        help_text='Perfil de acesso do usuário no fluxo de projetos'
    )
    telefone = models.CharField('Telefone / Ramal', max_length=30, blank=True)
    avatar = models.ImageField('Foto / Avatar', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'username']

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.get_cargo_display()})" if full_name else f"{self.username} ({self.get_cargo_display()})"

    @property
    def is_gestor(self):
        return self.cargo == self.CargoChoices.GESTOR or self.is_superuser

    @property
    def is_tecnico(self):
        return self.cargo == self.CargoChoices.TECNICO

    @property
    def is_vendedor(self):
        return self.cargo == self.CargoChoices.VENDEDOR

    @property
    def is_comercial(self):
        return self.cargo == self.CargoChoices.COMERCIAL
