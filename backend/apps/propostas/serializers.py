from rest_framework import serializers
from .models import Proposta, ConjuntoProposta, PropostaItem
from apps.catalogo.serializers import CatalogoItemSerializer

class PropostaItemSerializer(serializers.ModelSerializer):
    """
    Serializer para itens da BOM da proposta com suporte a estrutura em árvore.
    """
    catalogo_item_detalhes = CatalogoItemSerializer(source='catalogo_item', read_only=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    sub_itens = serializers.SerializerMethodField()

    class Meta:
        model = PropostaItem
        fields = [
            'id',
            'conjunto',
            'catalogo_item',
            'catalogo_item_detalhes',
            'parent',
            'quantidade',
            'preco_unitario_aplicado',
            'subtotal',
            'observacao_tecnica',
            'eh_subitem',
            'ordem',
            'sub_itens',
        ]
        read_only_fields = ['id', 'catalogo_item_detalhes', 'subtotal', 'eh_subitem', 'sub_itens']

    def get_sub_itens(self, obj):
        # Retorna apenas os filhos imediatos caso existam
        if obj.sub_itens.exists():
            return PropostaItemSerializer(obj.sub_itens.all(), many=True).data
        return []


class ConjuntoPropostaSerializer(serializers.ModelSerializer):
    """
    Serializer para conjuntos de itens (ex: Painel Elétrico, Suporte Mecânico).
    """
    itens = serializers.SerializerMethodField()
    total_conjunto = serializers.SerializerMethodField()

    class Meta:
        model = ConjuntoProposta
        fields = [
            'id',
            'proposta',
            'nome_conjunto',
            'descricao',
            'ordem',
            'itens',
            'total_conjunto',
        ]
        read_only_fields = ['id', 'itens', 'total_conjunto']

    def get_itens(self, obj):
        # Retorna apenas itens de topo (parent=None) para a árvore hierárquica
        top_itens = obj.itens.filter(parent__isnull=True).order_by('ordem')
        return PropostaItemSerializer(top_itens, many=True).data

    def get_total_conjunto(self, obj):
        total = sum((item.subtotal for item in obj.itens.all()), 0)
        return str(total)


class PropostaSerializer(serializers.ModelSerializer):
    """
    Serializer completo da Proposta com todos os conjuntos e itens da BOM.
    """
    status_proposta_display = serializers.CharField(source='get_status_proposta_display', read_only=True)
    conjuntos = ConjuntoPropostaSerializer(many=True, read_only=True)
    projeto_codigo = serializers.CharField(source='projeto.codigo_projeto_alfanumerico', read_only=True)

    class Meta:
        model = Proposta
        fields = [
            'id',
            'projeto',
            'projeto_codigo',
            'versao',
            'valor_total',
            'status_proposta',
            'status_proposta_display',
            'data_geracao',
            'observacoes',
            'conjuntos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'projeto_codigo', 'status_proposta_display', 'data_geracao', 'conjuntos', 'created_at', 'updated_at']
