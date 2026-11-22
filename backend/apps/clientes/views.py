from rest_framework import viewsets, permissions, filters
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de Clientes industriais com busca por nome, responsável e local aproximado.
    """
    queryset = Cliente.objects.all().order_by('nome_cliente')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome_cliente', 'responsavel_contato', 'local_aproximado', 'cnpj']
    ordering_fields = ['nome_cliente', 'created_at']
