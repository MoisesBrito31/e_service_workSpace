from rest_framework import viewsets, permissions, filters
from .models import OrdemServicoInstalacao, RelatorioServicoCampo
from .serializers import OrdemServicoInstalacaoSerializer, RelatorioServicoCampoSerializer

class OrdemServicoInstalacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento das Ordens de Serviço (OS) de campo.
    """
    queryset = OrdemServicoInstalacao.objects.select_related('projeto__cliente').prefetch_related('relatorios_campo').all().order_by('-data_abertura')
    serializer_class = OrdemServicoInstalacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['projeto__codigo_projeto_alfanumerico', 'escopo_servico', 'projeto__cliente__nome_cliente']
    ordering_fields = ['data_abertura', 'status_os']


class RelatorioServicoCampoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registro de relatórios de visitas de campo e fotos de evidência.
    """
    queryset = RelatorioServicoCampo.objects.select_related('ordem_servico__projeto', 'tecnico_responsavel').all().order_by('-data_visita')
    serializer_class = RelatorioServicoCampoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        os_id = self.request.query_params.get('os_id')
        if os_id:
            queryset = queryset.filter(ordem_servico_id=os_id)
        return queryset
