from rest_framework import serializers
from .models import FamiliaItem, CatalogoItem

class FamiliaItemSerializer(serializers.ModelSerializer):
    """
    Serializer das famílias base de produtos e serviços.
    """
    nome_display = serializers.CharField(source='get_nome_display', read_only=True)
    total_itens = serializers.IntegerField(source='itens.count', read_only=True)

    class Meta:
        model = FamiliaItem
        fields = ['id', 'nome', 'nome_display', 'descricao', 'total_itens']
        read_only_fields = ['id', 'nome_display', 'total_itens']


class CatalogoItemSerializer(serializers.ModelSerializer):
    """
    Serializer do Catálogo Central Único de Materiais e Serviços.
    Suporta formato: Modelo(CodigoIdentificador) -> Ex: QT50R-US-AF2Q(88383)
    """
    familia_nome = serializers.CharField(source='familia.get_nome_display', read_only=True)
    codigo_completo = serializers.CharField(read_only=True)

    class Meta:
        model = CatalogoItem
        fields = [
            'id',
            'familia',
            'familia_nome',
            'sku_codigo',
            'codigo_identificador',
            'codigo_completo',
            'nome',
            'especificacao_tecnica',
            'preco_base',
            'unidade_medida',
            'ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'familia_nome', 'codigo_completo', 'created_at', 'updated_at']
