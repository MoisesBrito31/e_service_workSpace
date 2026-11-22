from django.contrib import admin
from .models import Projeto, HistoricoStatus, ComentarioProjeto

class HistoricoStatusInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ('status_anterior', 'status_novo', 'usuario', 'data_mudanca', 'motivo_retorno', 'pausa_contagem_tempo')
    can_delete = False


class ComentarioProjetoInline(admin.TabularInline):
    model = ComentarioProjeto
    extra = 0
    readonly_fields = ('autor', 'created_at')


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_projeto_alfanumerico',
        'titulo',
        'cliente',
        'criado_por',
        'status',
        'created_at',
        'data_conclusao',
    )
    list_filter = ('status', 'created_at', 'cliente')
    search_fields = ('codigo_projeto_alfanumerico', 'titulo', 'descricao_demanda', 'cliente__nome_cliente')
    inlines = [HistoricoStatusInline, ComentarioProjetoInline]


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'status_anterior', 'status_novo', 'usuario', 'data_mudanca', 'pausa_contagem_tempo')
    list_filter = ('status_novo', 'pausa_contagem_tempo', 'data_mudanca')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'motivo_retorno')


@admin.register(ComentarioProjeto)
class ComentarioProjetoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'autor', 'created_at')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'conteudo')
    filter_horizontal = ('mencoes',)
