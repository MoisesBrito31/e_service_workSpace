from django.db import models
from apps.core.models import TimeStampedModel, BaseUUIDModel

class FamiliaItem(BaseUUIDModel):
    """
    Famílias base de produtos e serviços para categorização do catálogo central.
    """
    class FamiliaChoices(models.TextChoices):
        BANNER = 'BANNER', 'Banner Engineering'
        TURCK = 'TURCK', 'Turck'
        REDLION = 'REDLION', 'Red Lion'
        SMAC_MCA = 'SMAC_MCA', 'SMAC / MCA'
        WAGO = 'WAGO', 'Wago'
        ELETRICA = 'ELETRICA', 'Componentes Elétricos'
        MECANICA = 'MECANICA', 'Componentes Mecânicos'
        SERVICO = 'SERVICO', 'Serviços de Engenharia e Instalação'

    nome = models.CharField(
        'Família de Item',
        max_length=50,
        choices=FamiliaChoices.choices,
        unique=True
    )
    descricao = models.TextField('Descrição / Fabricante', blank=True)

    class Meta:
        verbose_name = 'Família de Item'
        verbose_name_plural = 'Famílias de Itens'
        ordering = ['nome']

    def __str__(self):
        return self.get_nome_display()


class CatalogoItem(TimeStampedModel):
    """
    Catálogo Central Único de Materiais, Equipamentos e Serviços da E-Service.
    Elimina a descentralização e divergência de tabelas antigas em Excel.
    Suporta identificação industrial no padrão: Modelo(CodigoIdentificador),
    exemplo: QT50R-US-AF2Q(88383) onde 88383 é o código identificador.
    """
    familia = models.ForeignKey(
        FamiliaItem,
        verbose_name='Família Base',
        related_name='itens',
        on_delete=models.PROTECT
    )
    sku_codigo = models.CharField(
        'Modelo / Part Number',
        max_length=100,
        db_index=True,
        help_text='Modelo ou Part Number do item (Ex: QT50R-US-AF2Q)'
    )
    codigo_identificador = models.CharField(
        'Código Identificador (Ident No. / ID)',
        max_length=50,
        blank=True,
        db_index=True,
        help_text='Código identificador numérico/alfanumérico (Ex: 88383)'
    )
    nome = models.CharField('Nome do Item / Descrição Curta', max_length=255, db_index=True)
    especificacao_tecnica = models.TextField(
        'Especificação Técnica Detalhada',
        help_text='Características elétricas, mecânicas, faixas de medição e comunicação'
    )
    preco_base = models.DecimalField('Preço Base (R$)', max_digits=12, decimal_places=2, default=0.00)
    unidade_medida = models.CharField('Unidade de Medida', max_length=10, default='UN')
    ativo = models.BooleanField('Item Ativo no Catálogo', default=True)

    class Meta:
        verbose_name = 'Item do Catálogo'
        verbose_name_plural = 'Itens do Catálogo'
        ordering = ['familia', 'sku_codigo', 'codigo_identificador']
        constraints = [
            models.UniqueConstraint(
                fields=['sku_codigo', 'codigo_identificador'],
                name='unique_sku_codigo_identificador'
            )
        ]

    @property
    def codigo_completo(self) -> str:
        """
        Retorna a identificação no formato padrão industrial: Modelo(Identificador)
        Exemplo: QT50R-US-AF2Q(88383)
        """
        if self.codigo_identificador:
            return f"{self.sku_codigo}({self.codigo_identificador})"
        return self.sku_codigo

    def __str__(self):
        return f"[{self.codigo_completo}] {self.nome} ({self.familia.get_nome_display()})"
