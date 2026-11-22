from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Projeto, HistoricoStatus, ComentarioProjeto
from .serializers import (
    ProjetoListSerializer,
    ProjetoDetailSerializer,
    ProjetoCreateSerializer,
    HistoricoStatusSerializer,
    ComentarioProjetoSerializer,
    MudarStatusSerializer,
)

class ProjetoViewSet(viewsets.ModelViewSet):
    """
    ViewSet central para gerenciamento do ciclo de vida dos Projetos Industriais.
    """
    queryset = Projeto.objects.select_related('cliente', 'criado_por', 'agenda_tecnica__tecnico').all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_projeto_alfanumerico', 'titulo', 'cliente__nome_cliente', 'cliente__responsavel_contato']
    ordering_fields = ['created_at', 'codigo_projeto_alfanumerico', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjetoListSerializer
        elif self.action == 'create':
            return ProjetoCreateSerializer
        return ProjetoDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        cliente_id = self.request.query_params.get('cliente_id')
        tecnico_id = self.request.query_params.get('tecnico_id')

        if status_param:
            queryset = queryset.filter(status=status_param)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if tecnico_id:
            queryset = queryset.filter(agenda_tecnica__tecnico_id=tecnico_id)
        return queryset

    @action(detail=True, methods=['post'])
    def mudar_status(self, request, pk=None):
        """
        Transiciona o status do projeto na Máquina de Estados, gravando histórico de SLA.
        Garante pausa do relógio quando o status_novo for AGUARDANDO_INFORMACAO.
        """
        projeto = self.get_object()
        serializer = MudarStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_novo = serializer.validated_data['status_novo']
        motivo = serializer.validated_data.get('motivo_retorno', '')
        status_anterior = projeto.status

        # Pausa o SLA se for aguardando informação
        deve_pausar = (status_novo == Projeto.StatusChoices.AGUARDANDO_INFORMACAO)

        # Atualiza o projeto
        projeto.status = status_novo
        if status_novo == Projeto.StatusChoices.CONCLUIDO:
            projeto.data_conclusao = timezone.now()
        projeto.save()

        # Atualiza o status da agenda se houver
        if hasattr(projeto, 'agenda_tecnica') and projeto.agenda_tecnica:
            agenda = projeto.agenda_tecnica
            from apps.agenda.models import AgendaTecnica
            if status_novo == Projeto.StatusChoices.EM_DESENVOLVIMENTO:
                agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.EM_ANDAMENTO
            elif status_novo == Projeto.StatusChoices.AGUARDANDO_INFORMACAO:
                agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.PAUSADO
            elif status_novo == Projeto.StatusChoices.CONCLUIDO:
                agenda.status_agenda = AgendaTecnica.StatusAgendaChoices.CONCLUIDO
            agenda.save()

        # Cria registro de rastreabilidade
        historico = HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=request.user,
            status_anterior=status_anterior,
            status_novo=status_novo,
            motivo_retorno=motivo,
            pausa_contagem_tempo=deve_pausar
        )

        return Response({
            'status': 'sucesso',
            'status_anterior': status_anterior,
            'status_novo': status_novo,
            'pausa_contagem_tempo': deve_pausar,
            'historico_id': str(historico.id)
        })

    @action(detail=True, methods=['get', 'post'])
    def comentarios(self, request, pk=None):
        """
        Lista ou adiciona comentários e discussões no card do projeto (estilo Planner).
        """
        projeto = self.get_object()

        if request.method == 'GET':
            comentarios = projeto.comentarios.select_related('autor').prefetch_related('mencoes').all()
            serializer = ComentarioProjetoSerializer(comentarios, many=True)
            return Response(serializer.data)

        # POST
        data = request.data.copy()
        data['projeto'] = projeto.id
        serializer = ComentarioProjetoSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comentario = serializer.save()
        return Response(ComentarioProjetoSerializer(comentario).data, status=status.HTTP_201_CREATED)
