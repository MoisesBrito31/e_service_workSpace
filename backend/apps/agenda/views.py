from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AgendaTecnica
from .serializers import AgendaTecnicaSerializer, AgendaTecnicaCreateUpdateSerializer
from apps.projetos.models import Projeto, HistoricoStatus

class AgendaTecnicaViewSet(viewsets.ModelViewSet):
    """
    ViewSet da Agenda Técnica e Fila de Desenvolvimento.
    Implementa as travas sequenciais e controle de SLA.
    """
    queryset = AgendaTecnica.objects.select_related('projeto__cliente', 'tecnico').all().order_by('tecnico', 'ordem_execucao')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AgendaTecnicaCreateUpdateSerializer
        return AgendaTecnicaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tecnico_id = self.request.query_params.get('tecnico_id')
        status_agenda = self.request.query_params.get('status_agenda')

        if tecnico_id:
            queryset = queryset.filter(tecnico_id=tecnico_id)
        if status_agenda:
            queryset = queryset.filter(status_agenda=status_agenda)
        return queryset

    @action(detail=False, methods=['get'])
    def minha_fila(self, request):
        """
        Retorna a fila de trabalho pessoal do técnico logado ordenada pela prioridade sequencial.
        """
        user = request.user
        fila = self.queryset.filter(tecnico=user).order_by('ordem_execucao')
        serializer = AgendaTecnicaSerializer(fila, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def iniciar_execucao(self, request, pk=None):
        """
        Inicia a execução técnica (Play).
        Aplica estritamente a Regra da Trava Sequencial da Fila.
        """
        agenda = self.get_object()

        # Validação da Trava Sequencial
        pode_iniciar, motivo_bloqueio = agenda.pode_iniciar()
        if not pode_iniciar:
            return Response(
                {
                    'erro': 'BLOQUEIO_TRAVA_SEQUENCIAL',
                    'mensagem': motivo_bloqueio,
                    'ordem_atual': agenda.ordem_execucao
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Transiciona o status da agenda e do projeto
        agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.EM_ANDAMENTO
        agenda.save()

        projeto = agenda.projeto
        status_anterior = projeto.status
        projeto.status = Projeto.StatusChoices.EM_DESENVOLVIMENTO
        projeto.save()

        # Registro no histórico
        HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo=projeto.status,
            motivo_retorno='Início de desenvolvimento pelo técnico respeitando a trava sequencial.',
            pausa_contagem_tempo=False
        )

        return Response({
            'status': 'sucesso',
            'mensagem': 'Projeto iniciado com sucesso na agenda.',
            'status_projeto': projeto.status,
            'status_agenda': agenda.status_agenda
        })

    @action(detail=True, methods=['post'])
    def pausar_execucao(self, request, pk=None):
        """
        Pausa o card por falta de dados técnicos (solicitação ao vendedor/comercial).
        Congela o relógio de SLA.
        """
        agenda = self.get_object()
        motivo = request.data.get('motivo', 'Aguardando informações técnicas complementares.')

        agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.PAUSADO
        agenda.save()

        projeto = agenda.projeto
        status_anterior = projeto.status
        projeto.status = Projeto.StatusChoices.AGUARDANDO_INFORMACAO
        projeto.save()

        # Grava no histórico com pausa do tempo ativada
        HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo=projeto.status,
            motivo_retorno=motivo,
            pausa_contagem_tempo=True
        )

        return Response({
            'status': 'sucesso',
            'mensagem': 'Projeto pausado e relógio de SLA congelado.',
            'status_projeto': projeto.status,
            'status_agenda': agenda.status_agenda
        })

    @action(detail=True, methods=['post'])
    def concluir_execucao(self, request, pk=None):
        """
        Conclui o trabalho técnico e avança o projeto para a Definição Comercial.
        """
        agenda = self.get_object()
        agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.CONCLUIDO
        agenda.save()

        projeto = agenda.projeto
        status_anterior = projeto.status
        projeto.status = Projeto.StatusChoices.DEFINICAO_COMERCIAL
        projeto.save()

        HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo=projeto.status,
            motivo_retorno='Desenvolvimento técnico concluído e enviado para definição comercial.',
            pausa_contagem_tempo=False
        )

        return Response({
            'status': 'sucesso',
            'mensagem': 'Entrega técnica concluída com sucesso.',
            'status_projeto': projeto.status,
            'status_agenda': agenda.status_agenda
        })
