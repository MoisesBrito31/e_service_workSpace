from django.db import models
from apps.core.models import TimeStampedModel

class Cliente(TimeStampedModel):
    """
    Entidade Cliente demandante dos projetos industriais.
    """
    nome_cliente = models.CharField('Nome do Cliente / Razão Social', max_length=200, db_index=True)
    responsavel_contato = models.CharField(
        'Responsável pelo Contato',
        max_length=150,
        help_text='Nome do contato direto na indústria (Ex: Sandro)'
    )
    local_aproximado = models.CharField(
        'Local Aproximado',
        max_length=200,
        help_text='Cidade / Bairro / Planta industrial (Ex: Piraquê - Madureira)'
    )
    email_contato = models.EmailField('E-mail de Contato', blank=True)
    telefone_contato = models.CharField('Telefone / WhatsApp', max_length=30, blank=True)
    cnpj = models.CharField('CNPJ', max_length=20, blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome_cliente']

    def __str__(self):
        return f"{self.nome_cliente} ({self.local_aproximado}) - Contato: {self.responsavel_contato}"
