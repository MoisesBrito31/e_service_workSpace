from django.contrib import admin
from .models import FamiliaItem, CatalogoItem

@admin.register(FamiliaItem)
class FamiliaItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome', 'descricao')


@admin.register(CatalogoItem)
class CatalogoItemAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_completo_display',
        'sku_codigo',
        'codigo_identificador',
        'nome',
        'familia',
        'preco_base',
        'unidade_medida',
        'ativo',
        'updated_at',
    )
    list_filter = ('familia', 'ativo', 'unidade_medida')
    search_fields = ('sku_codigo', 'codigo_identificador', 'nome', 'especificacao_tecnica')
    list_editable = ('preco_base', 'ativo')

    @admin.display(description='Identificação Padrão', ordering='sku_codigo')
    def codigo_completo_display(self, obj):
        return obj.codigo_completo
