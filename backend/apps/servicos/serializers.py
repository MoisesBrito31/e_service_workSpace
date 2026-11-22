from rest_framework import serializers
from .models import OrdemServicoInstalacao, RelatorioServicoCampo
from apps.authentication.serializers import UserSerializer

class RelatorioServicoCampoSerializer(serializers.ModelSerializer):
    """
    Serializer para os relatórios técnicos de atendimento e visita de campo.
    """
    tecnico_detalhes = UserSerializer(source='tecnico_responsavel', read_only=True)

    class Meta:
        model = RelatorioServicoCampo
        fields = [
            'id',
            'ordem_servico',
            'tecnico_responsavel',
            'tecnico_detalhes',
            'data_visita',
            'relatorio_campo',
            'evidencias_fotos',
            'created_at',
        ]
        read_only_fields = ['id', 'tecnico_detalhes', 'created_at']

    def create(self, validated_data):
        if 'tecnico_responsavel' not in validated_data:
            validated_data['tecnico_responsavel'] = self.context['request'].user
        return super().create(validated_data)


class OrdemServicoInstalacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para a Ordem de Serviço (OS) de montagem, instalação e pós-venda.
    """
    projeto_codigo = serializers.CharField(source='projeto.codigo_projeto_alfanumerico', read_only=True)
    cliente_nome = serializers.CharField(source='projeto.cliente.nome_cliente', read_only=True)
    status_os_display = serializers.CharField(source='get_status_os_display', read_only=True)
    relatorios_campo = RelatorioServicoCampoSerializer(many=True, read_only=True)

    class Meta:
        model = OrdemServicoInstalacao
        fields = [
            'id',
            'projeto',
            'projeto_codigo',
            'cliente_nome',
            'status_os',
            'status_os_display',
            'escopo_servico',
            'data_abertura',
            'relatorios_campo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'projeto_codigo', 'cliente_nome', 'status_os_display', 'data_abertura', 'relatorios_campo', 'created_at', 'updated_at']
