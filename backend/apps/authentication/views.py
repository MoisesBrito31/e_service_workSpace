from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateUpdateSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários e consulta de perfis.
    """
    queryset = User.objects.all().order_by('first_name', 'username')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna o perfil do usuário autenticado atual."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tecnicos(self, request):
        """Lista rápida apenas dos técnicos para atribuição de agenda pelo Gestor."""
        tecnicos = self.queryset.filter(cargo=User.CargoChoices.TECNICO, is_active=True)
        serializer = UserSerializer(tecnicos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mencoes(self, request):
        """Lista resumida de usuários ativos para autocomplete de menções (@usuario)."""
        usuarios = self.queryset.filter(is_active=True).values('id', 'username', 'first_name', 'last_name', 'cargo')
        return Response(list(usuarios))
