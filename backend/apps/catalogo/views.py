from rest_framework import viewsets, permissions, filters
from .models import FamiliaItem, CatalogoItem
from .serializers import FamiliaItemSerializer, CatalogoItemSerializer

class FamiliaItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listagem e consulta das 8 Famílias Base do Catálogo.
    """
    queryset = FamiliaItem.objects.all().order_by('nome')
    serializer_class = FamiliaItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class CatalogoItemViewSet(viewsets.ModelViewSet):
    """
    Gerenciamento e pesquisa do Catálogo Central Único.
    Suporta busca rápida por SKU, nome e especificação técnica.
    """
    queryset = CatalogoItem.objects.select_related('familia').all().order_by('familia', 'sku_codigo')
    serializer_class = CatalogoItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['sku_codigo', 'nome', 'especificacao_tecnica']
    ordering_fields = ['sku_codigo', 'nome', 'preco_base', 'updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        familia_id = self.request.query_params.get('familia_id')
        ativo = self.request.query_params.get('ativo')

        if familia_id:
            queryset = queryset.filter(familia_id=familia_id)
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo.lower() in ['true', '1'])
        return queryset
