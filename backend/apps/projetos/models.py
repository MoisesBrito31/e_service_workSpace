from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, BaseUUIDModel
from apps.clientes.models import Cliente

class Projeto(TimeStampedModel):
    """
    Entidade central de Projetos Industriais da E-Service.
    Implementa a Máquina de Estados e rastreabilidade ponta a ponta.
    """
    class StatusChoices(models.TextChoices):
        AGUARDANDO_AGENDAMENTO = 'AGUARDANDO_AGENDAMENTO', 'Aguardando Agendamento'
        EM_DESENVOLVIMENTO = 'EM_DESENVOLVIMENTO', 'Em Desenvolvimento'
        AGUARDANDO_INFORMACAO = 'AGUARDANDO_INFORMACAO', 'Aguardando Informação (Pausado)'
        DEFINICAO_COMERCIAL = 'DEFINICAO_COMERCIAL', 'Definição Comercial'
        INSTALACAO = 'INSTALACAO', 'Instalação / Serviços'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        CANCELADO = 'CANCELADO', 'Cancelado'

    codigo_projeto_alfanumerico = models.CharField(
        'Código do Projeto',
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Código alfanumérico único gerado pelo sistema (Ex: PR-132-01)'
    )
    titulo = models.CharField('Título Resumido da Demanda', max_length=200)
    descricao_demanda = models.TextField(
        'Descrição Detalhada da Demanda',
        help_text='Ex: Cliente necessita de um sistema que mede volume de um tanque de produtos químicos'
    )
    cliente = models.ForeignKey(
        Cliente,
        verbose_name='Cliente Demandante',
        related_name='projetos',
        on_delete=models.PROTECT
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Vendedor Solicitante',
        related_name='projetos_solicitados',
        on_delete=models.PROTECT
    )
    status = models.CharField(
        'Status Atual (Máquina de Estados)',
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.AGUARDANDO_AGENDAMENTO,
        db_index=True
    )
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)

    class Meta:
        verbose_name = 'Projeto Industrial'
        verbose_name_plural = 'Projetos Industriais'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo_projeto_alfanumerico} - {self.titulo} [{self.get_status_display()}]"


class HistoricoStatus(BaseUUIDModel):
    """
    Registro histórico de cada transição de status para auditoria e controle de SLA.
    Garante o congelamento do cronômetro quando status_novo == AGUARDANDO_INFORMACAO.
    """
    projeto = models.ForeignKey(
        Projeto,
        verbose_name='Projeto',
        related_name='historico_status',
        on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Usuário Responsável pela Mudança',
        related_name='historicos_transicao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status_anterior = models.CharField('Status Anterior', max_length=50)
    status_novo = models.CharField('Status Novo', max_length=50)
    data_mudanca = models.DateTimeField('Data da Mudança', auto_now_add=True)
    motivo_retorno = models.TextField(
        'Motivo do Retorno / Dúvida Técnica',
        blank=True,
        null=True,
        help_text='Justificativa caso o card volte para dúvidas ou comercial'
    )
    pausa_contagem_tempo = models.BooleanField(
        'Pausa Relógio SLA?',
        default=False,
        help_text='True quando o projeto transita para AGUARDANDO_INFORMACAO'
    )

    class Meta:
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Históricos de Status'
        ordering = ['-data_mudanca']

    def __str__(self):
        return f"{self.projeto.codigo_projeto_alfanumerico}: {self.status_anterior} -> {self.status_novo}"


class ComentarioProjeto(TimeStampedModel):
    """
    Comentários e discussões técnicas estilo Microsoft Planner no card do projeto.
    Suporta menções a usuários (@usuario).
    """
    projeto = models.ForeignKey(
        Projeto,
        verbose_name='Projeto',
        related_name='comentarios',
        on_delete=models.CASCADE
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Autor do Comentário',
        related_name='comentarios_realizados',
        on_delete=models.PROTECT
    )
    conteudo = models.TextField('Texto do Comentário')
    mencoes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Usuários Mencionados',
        related_name='comentarios_mencionado',
        blank=True
    )

    class Meta:
        verbose_name = 'Comentário do Projeto'
        verbose_name_plural = 'Comentários do Projeto'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.autor} em {self.projeto.codigo_projeto_alfanumerico} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
