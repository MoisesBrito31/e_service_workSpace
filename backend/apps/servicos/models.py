from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel, BaseUUIDModel
from apps.projetos.models import Projeto

class OrdemServicoInstalacao(TimeStampedModel):
    """
    Ordem de Serviço (OS) gerada no pós-venda após a aprovação comercial da proposta.
    """
    class StatusOSChoices(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        AGENDADA = 'AGENDADA', 'Instalação Agendada'
        EM_EXECUCAO = 'EM_EXECUCAO', 'Em Execução em Campo'
        FINALIZADA = 'FINALIZADA', 'Finalizada e Entregue'
        CANCELADA = 'CANCELADA', 'Cancelada'

    projeto = models.OneToOneField(
        Projeto,
        verbose_name='Projeto Associado',
        related_name='ordem_servico',
        on_delete=models.CASCADE
    )
    data_abertura = models.DateTimeField('Data de Abertura da OS', auto_now_add=True)
    status_os = models.CharField(
        'Status da Ordem de Serviço',
        max_length=30,
        choices=StatusOSChoices.choices,
        default=StatusOSChoices.ABERTA
    )
    escopo_servico = models.TextField(
        'Escopo dos Serviços de Campo',
        help_text='Descrição dos serviços de montagem, instalação elétrica, parametrização ou startup'
    )

    class Meta:
        verbose_name = 'Ordem de Serviço (OS)'
        verbose_name_plural = 'Ordens de Serviço (OS)'
        ordering = ['-data_abertura']

    def __str__(self):
        return f"OS #{self.projeto.codigo_projeto_alfanumerico} [{self.get_status_os_display()}]"


class RelatorioServicoCampo(BaseUUIDModel):
    """
    Relatórios de visitas e atendimentos em campo associados à OS.
    """
    ordem_servico = models.ForeignKey(
        OrdemServicoInstalacao,
        verbose_name='Ordem de Serviço',
        related_name='relatorios_campo',
        on_delete=models.CASCADE
    )
    tecnico_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Técnico de Campo',
        related_name='relatorios_campo_elaborados',
        on_delete=models.PROTECT
    )
    data_visita = models.DateField('Data do Atendimento / Visita')
    relatorio_campo = models.TextField('Relatório das Atividades Executadas')
    evidencias_fotos = models.JSONField(
        'Evidências e Fotos (URLs Object Storage)',
        default=list,
        blank=True,
        help_text='Lista de URLs ou caminhos das fotos de evidência em campo'
    )
    created_at = models.DateTimeField('Registrado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Relatório de Serviço de Campo'
        verbose_name_plural = 'Relatórios de Serviços de Campo'
        ordering = ['-data_visita', '-created_at']

    def __str__(self):
        return f"Relatório de Campo ({self.data_visita.strftime('%d/%m/%Y')}) - {self.ordem_servico.projeto.codigo_projeto_alfanumerico}"
