from rest_framework import serializers
from .models import AgendaTecnica
from apps.authentication.serializers import UserSerializer

class AgendaTecnicaSerializer(serializers.ModelSerializer):
    """
    Serializer para consulta da Agenda Técnica e Fila de Trabalho.
    """
    tecnico_detalhes = UserSerializer(source='tecnico', read_only=True)
    projeto_codigo = serializers.CharField(source='projeto.codigo_projeto_alfanumerico', read_only=True)
    projeto_titulo = serializers.CharField(source='projeto.titulo', read_only=True)
    cliente_nome = serializers.CharField(source='projeto.cliente.nome_cliente', read_only=True)
    status_agenda_display = serializers.CharField(source='get_status_agenda_display', read_only=True)
    bloqueado_por_trava = serializers.SerializerMethodField()

    class Meta:
        model = AgendaTecnica
        fields = [
            'id',
            'projeto',
            'projeto_codigo',
            'projeto_titulo',
            'cliente_nome',
            'tecnico',
            'tecnico_detalhes',
            'ordem_execucao',
            'data_programada',
            'horas_estimadas_sla',
            'horas_efetivas_gastas',
            'status_agenda',
            'status_agenda_display',
            'bloqueado_por_trava',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'projeto_codigo',
            'projeto_titulo',
            'cliente_nome',
            'tecnico_detalhes',
            'status_agenda_display',
            'bloqueado_por_trava',
            'created_at',
            'updated_at',
        ]

    def get_bloqueado_por_trava(self, obj) -> dict:
        pode, motivo = obj.pode_iniciar()
        return {
            'pode_iniciar': pode,
            'motivo': motivo
        }


class AgendaTecnicaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para o Gestor agendar, reordenar ou alterar tempos de SLA de um projeto.
    """
    class Meta:
        model = AgendaTecnica
        fields = [
            'id',
            'projeto',
            'tecnico',
            'ordem_execucao',
            'data_programada',
            'horas_estimadas_sla',
            'horas_efetivas_gastas',
            'status_agenda',
        ]
        read_only_fields = ['id']
