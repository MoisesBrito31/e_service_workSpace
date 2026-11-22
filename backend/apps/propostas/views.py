from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Proposta, ConjuntoProposta, PropostaItem
from .serializers import PropostaSerializer, ConjuntoPropostaSerializer, PropostaItemSerializer

class PropostaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para o gerenciamento de Propostas e versões da BOM.
    """
    queryset = Proposta.objects.select_related('projeto').prefetch_related('conjuntos__itens__catalogo_item').all().order_by('projeto', '-versao')
    serializer_class = PropostaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        projeto_id = self.request.query_params.get('projeto_id')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)
        return queryset

    @action(detail=True, methods=['post'])
    def recalcular(self, request, pk=None):
        """Recalcula o valor total da proposta somando todos os seus itens da BOM."""
        proposta = self.get_object()
        total = proposta.recalcular_total()
        return Response({
            'status': 'sucesso',
            'valor_total': str(total),
            'proposta_id': str(proposta.id),
            'versao': proposta.versao
        })

    @action(detail=True, methods=['post'])
    def nova_versao(self, request, pk=None):
        """
        Regra de Negócio Crítica (Versionamento de Artefatos):
        Gera uma nova versão incrementada (v2, v3...) a partir da versão atual,
        clonando todos os conjuntos, itens e subitens hierárquicos.
        """
        proposta_atual = self.get_object()
        projeto = proposta_atual.projeto

        # Próxima versão
        maior_versao = Proposta.objects.filter(projeto=projeto).order_by('-versao').first().versao
        nova_versao_numero = maior_versao + 1

        with transaction.atomic():
            nova_proposta = Proposta.objects.create(
                projeto=projeto,
                versao=nova_versao_numero,
                valor_total=proposta_atual.valor_total,
                status_proposta=Proposta.StatusPropostaChoices.RASCUNHO,
                observacoes=f"Revisão gerada a partir da versão v{proposta_atual.versao}."
            )

            # Clona conjuntos e itens
            for conjunto in proposta_atual.conjuntos.all():
                novo_conjunto = ConjuntoProposta.objects.create(
                    proposta=nova_proposta,
                    nome_conjunto=conjunto.nome_conjunto,
                    descricao=conjunto.descricao,
                    ordem=conjunto.ordem
                )

                # Mapeamento para preservar chave pai -> novo pai
                item_map = {}

                # 1. Copia itens de primeiro nível
                itens_pai = conjunto.itens.filter(parent__isnull=True)
                for item in itens_pai:
                    novo_item = PropostaItem.objects.create(
                        conjunto=novo_conjunto,
                        catalogo_item=item.catalogo_item,
                        quantidade=item.quantidade,
                        preco_unitario_aplicado=item.preco_unitario_aplicado,
                        observacao_tecnica=item.observacao_tecnica,
                        eh_subitem=False,
                        ordem=item.ordem
                    )
                    item_map[item.id] = novo_item

                # 2. Copia sub-itens associando ao novo pai
                sub_itens = conjunto.itens.filter(parent__isnull=False)
                for sub in sub_itens:
                    novo_pai = item_map.get(sub.parent_id)
                    PropostaItem.objects.create(
                        conjunto=novo_conjunto,
                        catalogo_item=sub.catalogo_item,
                        parent=novo_pai,
                        quantidade=sub.quantidade,
                        preco_unitario_aplicado=sub.preco_unitario_aplicado,
                        observacao_tecnica=sub.observacao_tecnica,
                        eh_subitem=True,
                        ordem=sub.ordem
                    )

            nova_proposta.recalcular_total()

        return Response(
            PropostaSerializer(nova_proposta).data,
            status=status.HTTP_201_CREATED
        )


class ConjuntoPropostaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Conjuntos de Itens dentro da Proposta.
    """
    queryset = ConjuntoProposta.objects.all().order_by('proposta', 'ordem')
    serializer_class = ConjuntoPropostaSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropostaItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Itens e Sub-itens da BOM da Proposta.
    """
    queryset = PropostaItem.objects.select_related('catalogo_item', 'conjunto').all().order_by('conjunto', 'ordem')
    serializer_class = PropostaItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        item = serializer.save()
        item.conjunto.proposta.recalcular_total()

    def perform_update(self, serializer):
        item = serializer.save()
        item.conjunto.proposta.recalcular_total()

    def perform_destroy(self, instance):
        proposta = instance.conjunto.proposta
        instance.delete()
        proposta.recalcular_total()
