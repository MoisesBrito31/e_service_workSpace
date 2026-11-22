from django.db import models
from decimal import Decimal
from apps.core.models import TimeStampedModel, BaseUUIDModel
from apps.projetos.models import Projeto
from apps.catalogo.models import CatalogoItem

class Proposta(TimeStampedModel):
    """
    Proposta Comercial com controle estrito de versões (v1, v2...) e status de revisão.
    """
    class StatusPropostaChoices(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho Técnico'
        ENVIADA_COMERCIAL = 'ENVIADA_COMERCIAL', 'Enviada para Análise Comercial'
        APROVADA = 'APROVADA', 'Aprovada pelo Comercial'
        REVISAO = 'REVISAO', 'Em Revisão Solicitada'

    projeto = models.ForeignKey(
        Projeto,
        verbose_name='Projeto Associado',
        related_name='propostas',
        on_delete=models.CASCADE
    )
    versao = models.PositiveIntegerField('Número da Versão', default=1)
    valor_total = models.DecimalField(
        'Valor Total da Proposta (R$)',
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status_proposta = models.CharField(
        'Status da Proposta',
        max_length=30,
        choices=StatusPropostaChoices.choices,
        default=StatusPropostaChoices.RASCUNHO
    )
    data_geracao = models.DateTimeField('Data de Geração', auto_now_add=True)
    observacoes = models.TextField('Observações Gerais da Proposta', blank=True)

    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['projeto', '-versao']
        constraints = [
            models.UniqueConstraint(
                fields=['projeto', 'versao'],
                name='unique_versao_proposta_por_projeto'
            )
        ]

    def __str__(self):
        return f"{self.projeto.codigo_projeto_alfanumerico} - Proposta v{self.versao} (R$ {self.valor_total}) [{self.get_status_proposta_display()}]"

    def recalcular_total(self):
        """
        Calcula o total somando apenas itens de nível superior (ou todos itens folha)
        para evitar contagem duplicada quando subitens compõem um item pai.
        """
        total = Decimal('0.00')
        for conjunto in self.conjuntos.all():
            for item in conjunto.itens.all():
                total += item.subtotal
        self.valor_total = total.quantize(Decimal('0.01'))
        self.save(update_fields=['valor_total'])
        return self.valor_total


class ConjuntoProposta(BaseUUIDModel):
    """
    Agrupamento funcional de itens dentro da proposta (Ex: Painel Elétrico Sistema de Visão 01, Conjunto Mecânico).
    """
    proposta = models.ForeignKey(
        Proposta,
        verbose_name='Proposta',
        related_name='conjuntos',
        on_delete=models.CASCADE
    )
    nome_conjunto = models.CharField(
        'Nome do Conjunto',
        max_length=200,
        help_text='Ex: Painel Elétrico Principal, Conjunto de Câmeras e Iluminação...'
    )
    descricao = models.TextField('Descrição / Detalhes do Conjunto', blank=True)
    ordem = models.PositiveIntegerField('Ordem de Exibição', default=1)

    class Meta:
        verbose_name = 'Conjunto da Proposta'
        verbose_name_plural = 'Conjuntos da Proposta'
        ordering = ['proposta', 'ordem']

    def __str__(self):
        return f"{self.proposta.projeto.codigo_projeto_alfanumerico} v{self.proposta.versao} - {self.nome_conjunto}"


class PropostaItem(BaseUUIDModel):
    """
    Item da BOM (Bill of Materials) da proposta com suporte a estrutura em árvore (sub-itens recursivos).
    Conecta obrigatoriamente ao CatalogoItem para garantir unicidade e confiabilidade de preços.
    """
    conjunto = models.ForeignKey(
        ConjuntoProposta,
        verbose_name='Conjunto',
        related_name='itens',
        on_delete=models.CASCADE
    )
    catalogo_item = models.ForeignKey(
        CatalogoItem,
        verbose_name='Item do Catálogo',
        related_name='proposta_itens',
        on_delete=models.PROTECT
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='Item Pai (Se for sub-item)',
        related_name='sub_itens',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Auto-relacionamento recursivo para permitir explosão de itens dentro de um item principal'
    )
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2, default=Decimal('1.00'))
    preco_unitario_aplicado = models.DecimalField(
        'Preço Unitário Aplicado (R$)',
        max_digits=12,
        decimal_places=2,
        help_text='Preço base do catálogo ou valor ajustado especificamente nesta proposta'
    )
    observacao_tecnica = models.TextField('Observação Técnica Específica', blank=True)
    eh_subitem = models.BooleanField('É Sub-item?', default=False)
    ordem = models.PositiveIntegerField('Ordem na Lista', default=1)

    class Meta:
        verbose_name = 'Item da Proposta (BOM)'
        verbose_name_plural = 'Itens da Proposta (BOM)'
        ordering = ['conjunto', 'ordem']

    def __str__(self):
        prefix = "-- " if self.eh_subitem else ""
        return f"{prefix}{self.quantidade}x [{self.catalogo_item.codigo_completo}] {self.catalogo_item.nome} = R$ {self.subtotal}"

    @property
    def subtotal(self) -> Decimal:
        return (self.quantidade * self.preco_unitario_aplicado).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        # Se possuir parent, marca automaticamente como subitem
        if self.parent:
            self.eh_subitem = True
        # Se preço unitário não foi fornecido, usa o preço base do catálogo
        if self.preco_unitario_aplicado is None and self.catalogo_item:
            self.preco_unitario_aplicado = self.catalogo_item.preco_base
        super().save(*args, **kwargs)
