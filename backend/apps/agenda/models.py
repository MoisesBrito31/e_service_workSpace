from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.projetos.models import Projeto

class AgendaTecnica(TimeStampedModel):
    """
    Governança da Agenda e Fila do Técnico gerida pelo Gestor.
    Implementa a Regra de Trava Sequencial e controle de SLA.
    """
    class StatusAgendaChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente na Fila'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        PAUSADO = 'PAUSADO', 'Pausado (Aguardando Informações)'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    projeto = models.OneToOneField(
        Projeto,
        verbose_name='Projeto Alocado',
        related_name='agenda_tecnica',
        on_delete=models.CASCADE
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Técnico Responsável',
        related_name='agendas_tecnicas',
        on_delete=models.PROTECT
    )
    ordem_execucao = models.PositiveIntegerField(
        'Ordem de Execução na Fila',
        default=1,
        help_text='Posição numérica na fila do técnico. Projetos com menor número têm prioridade.'
    )
    data_programada = models.DateField('Data Programada de Início')
    horas_estimadas_sla = models.DecimalField(
        'Horas Estimadas (Meta SLA)',
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    horas_efetivas_gastas = models.DecimalField(
        'Horas Efetivas Trabalhadas',
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    status_agenda = models.CharField(
        'Status da Agenda',
        max_length=20,
        choices=StatusAgendaChoices.choices,
        default=StatusAgendaChoices.PENDENTE
    )

    class Meta:
        verbose_name = 'Agenda Técnica'
        verbose_name_plural = 'Agendas Técnicas'
        ordering = ['tecnico', 'ordem_execucao']
        constraints = [
            models.UniqueConstraint(
                fields=['tecnico', 'ordem_execucao'],
                name='unique_ordem_por_tecnico'
            )
        ]

    def __str__(self):
        return f"[Fila #{self.ordem_execucao}] {self.tecnico.get_full_name() or self.tecnico.username} -> {self.projeto.codigo_projeto_alfanumerico}"

    def pode_iniciar(self) -> tuple[bool, str]:
        """
        Regra de Negócio Crítica (Trava Sequencial da Fila):
        O técnico não pode dar início (Play) em um projeto se houver outro projeto
        com ordem_execucao menor ainda pendente ou em andamento na sua agenda.
        """
        projetos_anteriores = AgendaTecnica.objects.filter(
            tecnico=self.tecnico,
            ordem_execucao__lt=self.ordem_execucao,
            status_agenda__in=[
                self.StatusAgendaChoices.PENDENTE,
                self.StatusAgendaChoices.EM_ANDAMENTO,
                self.StatusAgendaChoices.PAUSADO
            ]
        ).exclude(id=self.id).order_by('ordem_execucao')

        if projetos_anteriores.exists():
            primeiro_pendente = projetos_anteriores.first()
            return False, (
                f"Trava Sequencial: Você deve concluir ou liberar o projeto prioritário "
                f"#{primeiro_pendente.ordem_execucao} ({primeiro_pendente.projeto.codigo_projeto_alfanumerico}) "
                f"antes de iniciar este card."
            )
        return True, "Liberado para execução."
