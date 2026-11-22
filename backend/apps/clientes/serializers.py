from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para o cadastro e consulta de Clientes industriais.
    """
    total_projetos = serializers.IntegerField(source='projetos.count', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'nome_cliente',
            'responsavel_contato',
            'local_aproximado',
            'email_contato',
            'telefone_contato',
            'cnpj',
            'ativo',
            'total_projetos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'total_projetos', 'created_at', 'updated_at']
