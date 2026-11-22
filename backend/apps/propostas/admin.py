from django.contrib import admin
from .models import Proposta, ConjuntoProposta, PropostaItem

class PropostaItemInline(admin.TabularInline):
    model = PropostaItem
    extra = 1
    fields = ('catalogo_item', 'parent', 'quantidade', 'preco_unitario_aplicado', 'eh_subitem', 'ordem', 'observacao_tecnica')
    autocomplete_fields = ['catalogo_item']


class ConjuntoPropostaInline(admin.StackedInline):
    model = ConjuntoProposta
    extra = 1


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'versao', 'valor_total', 'status_proposta', 'data_geracao')
    list_filter = ('status_proposta', 'versao', 'data_geracao')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'projeto__titulo')
    inlines = [ConjuntoPropostaInline]


@admin.register(ConjuntoProposta)
class ConjuntoPropostaAdmin(admin.ModelAdmin):
    list_display = ('nome_conjunto', 'proposta', 'ordem')
    search_fields = ('nome_conjunto', 'proposta__projeto__codigo_projeto_alfanumerico')
    inlines = [PropostaItemInline]


@admin.register(PropostaItem)
class PropostaItemAdmin(admin.ModelAdmin):
    list_display = ('catalogo_item', 'conjunto', 'parent', 'quantidade', 'preco_unitario_aplicado', 'eh_subitem', 'ordem')
    list_filter = ('eh_subitem', 'conjunto__proposta__status_proposta')
    search_fields = ('catalogo_item__sku_codigo', 'catalogo_item__nome', 'observacao_tecnica')
    autocomplete_fields = ['catalogo_item', 'parent']
