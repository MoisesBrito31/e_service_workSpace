from django.contrib import admin
from .models import OrdemServicoInstalacao, RelatorioServicoCampo

class RelatorioServicoCampoInline(admin.StackedInline):
    model = RelatorioServicoCampo
    extra = 0


@admin.register(OrdemServicoInstalacao)
class OrdemServicoInstalacaoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'status_os', 'data_abertura', 'created_at')
    list_filter = ('status_os', 'data_abertura')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'escopo_servico')
    inlines = [RelatorioServicoCampoInline]


@admin.register(RelatorioServicoCampo)
class RelatorioServicoCampoAdmin(admin.ModelAdmin):
    list_display = ('ordem_servico', 'tecnico_responsavel', 'data_visita', 'created_at')
    list_filter = ('data_visita', 'tecnico_responsavel')
    search_fields = ('ordem_servico__projeto__codigo_projeto_alfanumerico', 'relatorio_campo')
