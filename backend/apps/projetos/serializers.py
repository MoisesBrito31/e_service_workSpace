from rest_framework import serializers
from .models import Projeto, HistoricoStatus, ComentarioProjeto
from apps.clientes.serializers import ClienteSerializer
from apps.authentication.serializers import UserSerializer

class HistoricoStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para o histórico de transições de status e pausas de SLA.
    """
    usuario_nome = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoStatus
        fields = [
            'id',
            'status_anterior',
            'status_novo',
            'data_mudanca',
            'motivo_retorno',
            'pausa_contagem_tempo',
            'usuario',
            'usuario_nome',
        ]
        read_only_fields = ['id', 'data_mudanca', 'usuario_nome']

    def get_usuario_nome(self, obj) -> str:
        return obj.usuario.get_full_name() or obj.usuario.username if obj.usuario else 'Sistema'


class ComentarioProjetoSerializer(serializers.ModelSerializer):
    """
    Serializer para comentários estilo Microsoft Planner com @menções.
    """
    autor_detalhes = UserSerializer(source='autor', read_only=True)
    mencoes_detalhes = UserSerializer(source='mencoes', many=True, read_only=True)

    class Meta:
        model = ComentarioProjeto
        fields = [
            'id',
            'projeto',
            'autor',
            'autor_detalhes',
            'conteudo',
            'mencoes',
            'mencoes_detalhes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'autor', 'autor_detalhes', 'mencoes_detalhes', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)


class ProjetoListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listagem de projetos em tabelas e cards Kanban.
    """
    cliente_nome = serializers.CharField(source='cliente.nome_cliente', read_only=True)
    cliente_local = serializers.CharField(source='cliente.local_aproximado', read_only=True)
    cliente_contato = serializers.CharField(source='cliente.responsavel_contato', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    vendedor_nome = serializers.CharField(source='criado_por.get_full_name', read_only=True)
    tecnico_alocado = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'codigo_projeto_alfanumerico',
            'titulo',
            'status',
            'status_display',
            'cliente',
            'cliente_nome',
            'cliente_local',
            'cliente_contato',
            'criado_por',
            'vendedor_nome',
            'tecnico_alocado',
            'created_at',
            'data_conclusao',
        ]

    def get_tecnico_alocado(self, obj):
        if hasattr(obj, 'agenda_tecnica') and obj.agenda_tecnica:
            tecnico = obj.agenda_tecnica.tecnico
            return {
                'id': tecnico.id,
                'nome': tecnico.get_full_name() or tecnico.username,
                'ordem_execucao': obj.agenda_tecnica.ordem_execucao,
                'status_agenda': obj.agenda_tecnica.status_agenda,
            }
        return None


class ProjetoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado com dados completos do cliente, histórico e comentários.
    """
    cliente = ClienteSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    criado_por = UserSerializer(read_only=True)
    historico_status = HistoricoStatusSerializer(many=True, read_only=True)
    comentarios = ComentarioProjetoSerializer(many=True, read_only=True)
    agenda_tecnica_detalhes = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'codigo_projeto_alfanumerico',
            'titulo',
            'descricao_demanda',
            'status',
            'status_display',
            'cliente',
            'criado_por',
            'data_conclusao',
            'agenda_tecnica_detalhes',
            'historico_status',
            'comentarios',
            'created_at',
            'updated_at',
        ]

    def get_agenda_tecnica_detalhes(self, obj):
        if hasattr(obj, 'agenda_tecnica') and obj.agenda_tecnica:
            from apps.agenda.serializers import AgendaTecnicaSerializer
            return AgendaTecnicaSerializer(obj.agenda_tecnica).data
        return None


class ProjetoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para o cadastro inicial da requisição pelo Vendedor.
    """
    class Meta:
        model = Projeto
        fields = [
            'id',
            'codigo_projeto_alfanumerico',
            'titulo',
            'descricao_demanda',
            'cliente',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['criado_por'] = user
        validated_data['status'] = Projeto.StatusChoices.AGUARDANDO_AGENDAMENTO
        projeto = super().create(validated_data)

        # Registro inicial no histórico
        HistoricoStatus.objects.create(
            projeto=projeto,
            usuario=user,
            status_anterior='INICIO',
            status_novo=projeto.status,
            motivo_retorno='Criação inicial da requisição pelo vendedor.',
            pausa_contagem_tempo=False
        )
        return projeto


class MudarStatusSerializer(serializers.Serializer):
    """
    Serializer para mudança de status com controle estrito de máquina de estados.
    """
    status_novo = serializers.ChoiceField(choices=Projeto.StatusChoices.choices)
    motivo_retorno = serializers.CharField(required=False, allow_blank=True, default='')
