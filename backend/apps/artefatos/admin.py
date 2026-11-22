from django.contrib import admin
from .models import RelatorioDescritivo, Topologia

@admin.register(RelatorioDescritivo)
class RelatorioDescritivoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'versao', 'titulo', 'arquivo_docx', 'arquivo_pdf', 'created_at')
    list_filter = ('versao', 'created_at')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'titulo')


@admin.register(Topologia)
class TopologiaAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'nome_arquivo', 'arquivo', 'data_upload')
    search_fields = ('projeto__codigo_projeto_alfanumerico', 'nome_arquivo', 'descricao_explicativa')
